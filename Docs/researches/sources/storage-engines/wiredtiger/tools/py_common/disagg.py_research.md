# sources/storage-engines/wiredtiger/tools/py_common/disagg.py

Purpose: provides the common disaggregated-storage page decoding model used by both page-service JSON input and SQLite page-log input. It wraps page metadata and bytes, tracks table-level full/delta counts, and validates delta-chain ordering before delegating to the generic B-tree page decoder.

Important APIs and control flow: `UpdateTypeFlags` mirrors page service update-type constants. `Metadata` carries `lsn`, `page_id`, `table_id`, optional `base_lsn`/`backlink_lsn`, and a `delta` flag; `is_metadata_page()` treats table id 1 as a metadata file. `DisaggTableSummary.update_with_page()` accumulates full vs delta pages. `process_disagg_pages()` iterates a list of per-page chains, prints metadata, special-cases metadata pages by extracting an `addr="..."` root address, parses normal pages through `btree_format.WTPage.parse(disagg=True)`, validates base/delta magic numbers, validates previous checksum links within a delta chain, warns on write-generation ordering, prints either headers or full page contents, and returns the summary.

State and persistence behavior: no persistent state is written. The only mutable runtime state is the current `delta_chain` and the accumulated `DisaggTableSummary`. Output is written to stdout through `Printer`.

Dependencies and integration points: depends on `binary_data.BinaryFile`, `btree_format.WTPage`, `btree_format.BlockDisaggHeader`, `btree_format.DisaggAddr`, `DecodeOptions`, and `Printer`. It is called by `py_common.page_service.process_disagg_table()` and `py_common.sqlite_format.process_sqlite_file()`.

Risks: metadata-page parsing assumes an ASCII metadata string containing `addr="..."`; malformed metadata raises rather than producing a graceful diagnostic. Delta-chain validation logs errors but does not fail decoding. The write-generation ordering check is only as reliable as input ordering, which differs across page-service and SQLite sources. Metadata table id 1 is a convention embedded in code.

Test signals: `test_decode_disagg_delta_chain.py` expects one full-image block and ten delta blocks from a log dump. `test_decode_disagg_table.py` validates full/delta totals for encrypted page-service JSONL when `DISAGG_KEYFILE` is configured. `test_sqlite_format.py` exercises SQLite-to-`DisaggPage` chain construction.
