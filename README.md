# Vietnamese robot-vacuum comments NLP

Reproducible CPU pipeline for **only** the `comments` worksheet and `text` column of the original Excel workbook. The workbook is read-only. No paid APIs or API keys are needed.

## Install

Python 3.12 is the tested runtime. Install CPU PyTorch first to avoid downloading CUDA dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install torch==2.6.0 --index-url https://download.pytorch.org/whl/cpu
python -m pip install -r requirements.txt
python -m pip check
```

In the prepared cloud machine, use `source /workspace/.venvs/robot-nlp/bin/activate` instead. Run commands from the repository root. Set `HF_HOME`, `XDG_CACHE_HOME`, `MPLCONFIGDIR`, and `NUMBA_CACHE_DIR` to writable cache directories when needed; the cloud runner defaults to `/workspace/.cache` locations. There are no background services.

Required network destinations: PyPI and CPU PyTorch indexes for installation; `huggingface.co` and Hugging Face artifact destinations (`cdn-lfs.huggingface.co`, `cdn-lfs.hf.co`, `cas-bridge.xethub.hf.co`, `cas-server.xethub.hf.co`, `us.aws.cdn.hf.co`) for pretrained models. The last host was observed in the real weights redirect. The runner defaults to the supported HTTP downloader (`HF_HUB_DISABLE_XET=1`) for proxy compatibility; TLS verification remains enabled. Network denials are fatal to model analysis. Do not disable TLS or substitute guessed scores.

## Execute

```bash
python src/run_nlp.py --input robothutbui_facebookscrape.xlsx --sheet comments --output outputs --seed 42
```

Omit `--input` to discover the unique matching workbook anywhere in this checkout. `--min-chars 1` retains short meaningful comments; this threshold is configurable. `--batch-size 16` is CPU friendly. Existing output files are protected unless `--overwrite` is explicit; the runner refuses to remove unrelated files even then. Do not run two processes into the same output directory.

Model defaults:

- `wonrax/phobert-base-vietnamese-sentiment`: Vietnamese PhoBERT classifier; load its actual semantic `id2label` mapping and model card. Only explicit positive/neutral/negative labels are accepted. Input is segmented with underthesea, preserving negation and emoji. Score = P(positive) − P(negative). Long inputs are truncated to at most 256 tokens; count is logged. Probabilities are not validated accuracy.
- `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`: multilingual sentence embeddings of complete minimally cleaned sentences, without stopword stripping. Seeded UMAP + HDBSCAN + BERTopic use corpus-size-adaptive parameters. Vietnamese segmentation and a small explicit stopword list apply only to CountVectorizer representations. The embeddings model's own maximum sequence length can truncate long comments.

The first successful run resolves model commits and records them in `run_metadata.json`. Reproduce that run with `--sentiment-revision SHA --embedding-revision SHA` and the package versions in metadata. Model cards are copied into outputs. Torch, NumPy, Python and UMAP are seeded; deterministic Torch operations and bounded CPU threads are used. Hardware/library differences and BERTopic clustering can affect results; no stability across seeds is claimed.

## Cleaning and interpretation

Every original row has its Excel row number (`source_row_id`), normalized masked text, commercial evidence and one mutually exclusive `cleaning_status`. Null/blank, normalized exact duplicates, below-minimum texts, pure commercial and uncertain rows are excluded in that order. Duplicate flags are separately reported. No near-duplicate removal is performed. Raw text exists only transiently in memory and is never exported.

Commercial rules require multiple signals and distinguish `organic`, `commercial`, `mixed_commercial`, and `uncertain`. Brands, price, repair and warranty words alone do not classify a message as spam. Primary analysis keeps organic and issue-bearing mixed messages; separable sales-only sentences are removed from mixed model input when possible. The masked full comment remains available for audit. Ambiguous single-signal messages are flagged uncertain and excluded pending review. Rules are heuristics. Organic-only sensitivity reuses primary topic assignments and changes the denominator; it does not refit clusters.

Topic -1 is retained as Other / Unassigned in every denominator. Topic names are proposed using keywords **and representative sentences**, marked as requiring human review. Membership strengths are not calibrated topic probabilities. Business evidence categories are explicit overlapping lexical mention counts, distinct from BERTopic assignments. Reports separate measured mentions from opportunity hypotheses; discussions do not establish purchase causality or unique-customer shares.

## Outputs and validation

A successful run produces every artifact requested by `CODEX_INSTRUCTIONS_ROBOT_VACUUM_NLP.md`, plus `sentiment_review_sample.csv`, `sensitivity_results.csv`, `business_evidence.csv`, model cards, `model_smoke_predictions.csv`, and `validation.json`. CSVs are UTF-8 with BOM; PNGs are 180 dpi and use DejaVu Sans for Vietnamese.

The runner verifies original-input SHA-256, counts including outliers, per-topic crosstab consistency, probability/score consistency, missing results, exported phone/email/handle masking, CSV encoding, and PNG integrity/resolution. It prints absolute output paths. A `.incomplete` marker, failure.txt, and metadata status `failed` indicate an incomplete run; partial audit files are **not** sentiment/topic findings. Stale results are removed only with explicit overwrite.

Run meaningful offline regression checks:

```bash
python -m pytest -q
python src/verify_outputs.py --output outputs
```

For a model-blocked run, use `python src/verify_outputs.py --output outputs --audit-only` to check only the input hash, audit accounting, review membership and export privacy. It explicitly does not validate sentiment or topics. A blocked run's Vietnamese `report.md` reports audit counts and the blocker, and contains no model findings.

Human review is still required: `commercial_review_sample.csv` provides stratified commercial examples; `sentiment_review_sample.csv` samples up to 100 predictions across mixed content, uncertainty, negation, diagnostics, possible sarcasm and predicted labels. `human_*` columns start empty. No human validation or accuracy is claimed until actual labels are supplied. Inspect model smoke predictions and topic labels before using the report for decisions.

## Execution status

See `outputs/run_metadata.json` and `outputs/failure.txt` for the actual most recent attempt. If Hugging Face is denied by the cloud proxy, apply the required network domains in environment settings, then rerun with `--overwrite`. This deliberately stops after the audit rather than inventing model inference, charts or business findings.
