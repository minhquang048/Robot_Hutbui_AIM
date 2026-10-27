"""Real pretrained inference only. Missing model access is a hard error."""
import re
import numpy as np
import torch
from huggingface_hub import HfApi, hf_hub_download
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from sentence_transformers import SentenceTransformer
from underthesea import word_tokenize
from sklearn.feature_extraction.text import CountVectorizer
from umap import UMAP
from hdbscan import HDBSCAN
from bertopic import BERTopic

SENTIMENT_MODEL='wonrax/phobert-base-vietnamese-sentiment'
EMBEDDING_MODEL='sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2'
STOPWORDS=['là','và','của','thì','mà','các','những','một','này','đó','với','cho','có','được','ạ','ơi','nhé','nha','em','mình','bạn','anh','chị']

def segment(text):
    return word_tokenize(text,format='text')

def topic_tokens(text):
    return re.findall(r'\b[^\W\d_][\w]*\b', segment(text.lower()))

def load_models(args,out=None):
    api=HfApi()
    info={}
    try:
        for key, model, requested in [('sentiment',args.sentiment_model,args.sentiment_revision),('embedding',args.embedding_model,args.embedding_revision)]:
            print('Resolving model:', model, flush=True)
            meta=api.model_info(model,revision=requested)
            info[key]={'id':model,'revision':meta.sha}
            card=hf_hub_download(model,'README.md',revision=meta.sha)
            with open(card,encoding='utf-8') as f: info[key]['model_card']=f.read()
            if out is not None: (out/(key+'_model_card.md')).write_text(info[key]['model_card'],encoding='utf-8')
        sm=info['sentiment']; em=info['embedding']
        print('Loading sentiment weights through verified HTTPS', flush=True)
        tok=AutoTokenizer.from_pretrained(sm['id'],revision=sm['revision'],use_fast=False)
        classifier=AutoModelForSequenceClassification.from_pretrained(sm['id'],revision=sm['revision'],use_safetensors=False if sm['id']==SENTIMENT_MODEL else None).to('cpu').eval()
        print('Loading multilingual embedding weights', flush=True)
        embedder=SentenceTransformer(em['id'],revision=em['revision'],device='cpu')
    except Exception as e:
        # Avoid persisting expiring signed artifact URLs from nested download errors.
        hosts=sorted(set(re.findall(r'(?:host=\x27|https?://)([a-zA-Z0-9.-]+)',str(e))))
        detail='proxy/access denied (403)' if '403' in str(e) else type(e).__name__
        error=RuntimeError('Pretrained model download/load failed: '+detail+'; hosts='+','.join(hosts)+'. No sentiment scores or topics were fabricated. Check Hugging Face network access/cache.')
        error.model_info={k:{field:value for field,value in data.items() if field!='model_card'} for k,data in info.items()}
        raise error from e
    mapping={}
    aliases={'pos':'positive','positive':'positive','neg':'negative','negative':'negative','neu':'neutral','neutral':'neutral'}
    for idx,label in classifier.config.id2label.items():
        norm=str(label).lower().strip()
        if norm not in aliases:
            raise ValueError(f'Unverified sentiment label {label!r}. Inspect model card and supply a model with explicit semantic labels.')
        mapping[int(idx)]=aliases[norm]
    if set(mapping.values()) != {'positive','neutral','negative'} or len(mapping)!=3:
        raise ValueError('This pipeline requires an explicit three-class Vietnamese model; no unvalidated neutral heuristic is used.')
    info['sentiment']['id2label']=classifier.config.id2label
    info['sentiment']['score_definition']='P(positive) - P(negative)'
    info['sentiment']['preprocessing']='underthesea word segmentation; no stopword removal; truncation at model/tokenizer maximum'
    info['sentiment']['domain_note']='Fine-tuned on 30K e-commerce reviews (model card); domain differs from Facebook robot vacuum comments. No validated accuracy claimed.'
    info['embedding']['max_seq_length']=embedder.max_seq_length
    info['embedding']['dimension']=embedder.get_sentence_embedding_dimension()
    return tok,classifier,embedder,mapping,info

def infer_sentiment(texts,tok,classifier,mapping,batch_size):
    values=[]
    max_length=min(int(getattr(tok,'model_max_length',256)),int(getattr(classifier.config,'max_position_embeddings',258))-2,256)
    truncated=0
    with torch.inference_mode():
        for offset in range(0,len(texts),batch_size):
            batch=[segment(t) for t in texts[offset:offset+batch_size]]
            truncated+=sum(len(tok.encode(t,add_special_tokens=True))>max_length for t in batch)
            encoded=tok(batch,padding=True,truncation=True,max_length=max_length,return_tensors='pt')
            probs=classifier(**encoded).logits.softmax(dim=-1).cpu().numpy()
            for p in probs:
                row={'p_'+mapping[i]:float(v) for i,v in enumerate(p)}
                row.update(sentiment_label=mapping[int(p.argmax())],sentiment_confidence=float(p.max()),sentiment_score=row['p_positive']-row['p_negative'])
                values.append(row)
    return values,{'sentiment_max_length':max_length,'sentiment_truncated_count':truncated}

def cluster(texts,embedder,seed,batch_size):
    n=len(texts)
    if n<6: raise ValueError('Fewer than six retained comments; insufficient for meaningful BERTopic clustering.')
    minimum=max(3,min(30,round(n**0.5/2)))
    params=dict(min_topic_size=minimum,min_cluster_size=minimum,n_neighbors=min(15,n-1),min_df=1 if n<100 else 2,n_components=min(5,n-2))
    params['embedding_truncated_count']=sum(len(embedder.tokenizer.encode(t,add_special_tokens=True))>embedder.max_seq_length for t in texts)
    embeddings=embedder.encode(texts,batch_size=batch_size,show_progress_bar=True,normalize_embeddings=True,convert_to_numpy=True)
    model=BERTopic(embedding_model=embedder,language='multilingual',min_topic_size=minimum,
        umap_model=UMAP(n_neighbors=params['n_neighbors'],n_components=params['n_components'],min_dist=0.0,metric='cosine',random_state=seed,n_jobs=1),
        hdbscan_model=HDBSCAN(min_cluster_size=minimum,min_samples=max(2,minimum//2),metric='euclidean',cluster_selection_method='eom',prediction_data=True,core_dist_n_jobs=2),
        vectorizer_model=CountVectorizer(tokenizer=topic_tokens,token_pattern=None,stop_words=STOPWORDS,min_df=params['min_df'],ngram_range=(1,2)),calculate_probabilities=False,verbose=True)
    topics,probabilities=model.fit_transform(texts,embeddings)
    if probabilities is None: probabilities=np.full(n,np.nan)
    elif np.asarray(probabilities).ndim>1: probabilities=np.asarray(probabilities).max(axis=1)
    return model,topics,probabilities,params
