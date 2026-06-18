# sources/storage-engines/wiredtiger/tools/py_common/page_service.py

Purpose: adapts Object Read Proxy/GetTableAtLSN JSONL output into decrypted `DisaggPage` objects for the disaggregated page decoder.

Important APIs and control flow: `extract_value()` unwraps typed metadata values from page-service JSON. `parse_metadata()` extracts page `lsn`, required `flags`, `page_id`, `table_id`, and optional `base_lsn`/`backlink_lsn`, mapping the delta flag to `disagg.Metadata`. `decrypt_page()` validates the external `pagedecryptor` binary and keyfile, writes page entry bytes as base64 to a temporary input, invokes `pagedecryptor` with page identity and chain metadata, and reads decrypted bytes from a temporary output. `process_disagg_table()` reads JSONL lines, converts each `entries` list into a page chain, skips empty entries, decrypts non-empty pages, and calls `disagg.process_disagg_pages()`.

State and persistence behavior: creates temporary files for decryption and deletes them automatically. It does not mutate source files or database state. It logs decryptor stdout/stderr at debug level and returns a `DisaggTableSummary`.

Dependencies and integration points: depends on MongoDB's external `pagedecryptor`, a KEK keyfile, `base64`, `json`, `subprocess`, `tempfile`, `DecodeOptions.keyfile`, and `py_common.disagg`. It is invoked from `wt_binary_decode` via `--disagg-table`.

Risks: decryption is unavailable unless the MongoDB encryption module tool is built and on `PATH`. Every page incurs a subprocess call, which is expensive for large tables. Metadata unwrapping assumes a single value inside `metadata[key]["val"]`. The temporary output file is opened before the subprocess writes it; this works for normal files but is sensitive to platform semantics. Decrypt failures propagate after logging.

Test signals: `test_decode_disagg_table.py` skips unless `DISAGG_KEYFILE` is set, then expects 8 total pages, 2 delta pages, and 6 full pages from `disagg_oplog.jsonl`.
