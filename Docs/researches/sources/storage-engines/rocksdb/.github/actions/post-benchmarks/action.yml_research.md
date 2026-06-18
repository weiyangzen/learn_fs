<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/.github/actions/post-benchmarks/action.yml -->
# Research: sources/storage-engines/rocksdb/.github/actions/post-benchmarks/action.yml

Purpose: Uploads benchmark result artifacts and attempts to send a benchmark report to an external visualization endpoint.

Important APIs/types/functions: uses `actions/upload-artifact@v4.0.0` for `benchmark-results`; runs `benchmark_log_tool.py --tsvfile ... --esdocument ...`.

Control flow: artifact upload is required with `if-no-files-found: error`; the external report step disables immediate failure and ends with `true`, making visualization submission best-effort.

State and persistence behavior: persists benchmark files as GitHub artifacts and may write documents to an external Elasticsearch endpoint.

Dependencies and integration points: follows `perform-benchmarks` in `benchmark-linux.yml`; depends on `report.tsv`, Python tooling, network access, and the configured search endpoint.

Risks: external upload failures are intentionally hidden, so dashboards can silently miss data. The endpoint URL is embedded in workflow code.

Test signals: artifact upload success is hard CI signal; visualization ingestion must be checked in external systems/logs.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/.github/actions/post-benchmarks/action.yml -->
