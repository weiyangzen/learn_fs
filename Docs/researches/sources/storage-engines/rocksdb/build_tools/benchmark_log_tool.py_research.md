# sources/storage-engines/rocksdb/build_tools/benchmark_log_tool.py research

Purpose: `benchmark_log_tool.py` parses RocksDB benchmark TSV output and optionally uploads sanitized benchmark records to an OpenSearch/Elasticsearch document endpoint.

Important APIs: `Configuration` reads `ES_USER` and `ES_PASS` at class-definition time. `BenchmarkResultException` carries parser error content. `BenchmarkUtils.sanity_check(row)` validates required benchmark fields, integer `ops_sec`, and parseable dates. `BenchmarkUtils.conform_opensearch(row)` normalizes date fields and replaces dots in keys. `ResultParser` tokenizes benchmark lines with configurable field, whitespace, and separator regexes. Top-level functions include `load_report_from_tsv()`, `push_report_to_opensearch()`, and `push_report_to_null()`.

Control flow: the CLI parses `--tsvfile`, `--esdocument`, and `--upload`. The TSV loader reads all lines and parses records using the first non-comment row as the header. Upload mode filters rows through `sanity_check()`, conforms them, posts each JSON record using `requests.post()`, and raises on HTTP errors. Null mode validates and logs the conformed records without network writes.

State and persistence: local state is in parsed row dictionaries, which are mutated by `conform_opensearch()`. Persistence is external: HTTP writes to OpenSearch and log output. Credentials are read from environment variables.

Dependencies and integration: external dependencies are `requests` and `python-dateutil`. The script is aimed at benchmark automation, historically CircleCI scraper inputs, and OpenSearch graphing.

Risks and test signals: importing the module without `ES_USER`/`ES_PASS` can fail because `Configuration` reads environment variables eagerly even if upload is disabled. Parser behavior is custom and may mishandle quoted TSV fields. Upload performs one POST per row with no retry/backoff. Tests should cover TSV parsing edge cases, bad rows, date normalization, null upload, missing credentials, and mocked HTTP status failures.
