# sources/storage-engines/wiredtiger/tools/wt_binary_decode.py

Purpose: top-level command-line decoder for WiredTiger binary data, including `.wt` files, hex dumps embedded in logs, disaggregated page-service JSONL, and SQLite page-log files.

Important APIs and control flow: `open_input_file()` supports stdin for text or binary modes. `decode_dumpin_input()`, `decode_disagg_table_input()`, `decode_sqlite_input()`, and `decode_wt_binary_input()` route to specialized helpers. `wtdecode()` selects dump-in first, then explicit disagg-table, then automatic SQLite signature detection, otherwise ordinary WT binary decode. `feature_check()` warns about missing BSON, Snappy, and CRC32C support. `get_arg_parser()` defines CLI options for version, input mode, BSON, disagg flags, offset, page id, LSN, page count, skip-data, keyfile, verbosity, byte/split output, CSV output, and continue-on-checksum-failure. The `__main__` block configures logging, opens optional CSV output, builds `DecodeOptions`, and handles keyboard/broken-pipe exits.

State and persistence behavior: read-only over decode input. Optional CSV output writes to the path from `--csv`. The tool prints decoded content to stdout and logs warnings/errors.

Dependencies and integration points: orchestrates `py_common.mdb_log_parse`, `binary_data`, `btree_format`, `snappy_util`, `file_format`, `page_service`, and `sqlite_format`. It is the primary entry point exercised by the decode tests.

Risks: SQLite auto-detection opens the filename and does not apply to stdin. Optional dependency warnings do not always prevent later hard failures, especially for Snappy-compressed pages. Some options are mode-specific but accepted globally, so invalid combinations rely on downstream behavior. Disaggregated table decryption needs external `pagedecryptor` and keyfile.

Test signals: tests in this subset cover ordinary page decode, dump-in disagg delta-chain decode, MongoDB corrupt-log diagnostics, and page-service JSONL decode when environment prerequisites exist.
