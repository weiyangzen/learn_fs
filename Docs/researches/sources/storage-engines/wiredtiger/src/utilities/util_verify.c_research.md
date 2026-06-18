<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/utilities/util_verify.c -->
# sources/storage-engines/wiredtiger/src/utilities/util_verify.c

Purpose: Implements `wt verify`, validating one table/layered object or all table/layered metadata entries with configurable diagnostic dump and timestamp options.

Important APIs/functions: `usage` lists verification controls. `verify_one` delegates to `session->verify(session, uri, config)` and handles verbose progress newline. `util_verify` builds a WiredTiger config string in a scratch buffer, supporting `read_corrupt`, dump modes (`dump_address`, `dump_blocks`, `dump_layout`, `dump_tree_shape`, `dump_offsets=[...]`, `dump_pages`), `dump_key_data`, `strict`, `stable_timestamp`, `do_not_clear_txn_id`, and `dump_all_data`.

Control flow: It allocates a session scratch buffer with `__wt_scr_alloc`, parses options with `__wt_getopt`, rejects simultaneous `-u` and `-k`, and then either verifies a resolved table URI or opens `metadata:` to enumerate all keys. In all-table mode it only verifies keys prefixed `table:` or `layered:` and either aborts on the first non-`ENOTSUP` error when `-a` is set or accumulates errors with `WT_TRET`.

State and persistence behavior: Verification is primarily read/validation, but options such as `do_not_clear_txn_id` imply default verification may clear transaction IDs as part of repair/cleanup semantics inside WiredTiger. Dump options can expose key or full application data depending on `-k`/`-u`.

Dependencies and integration points: Uses public `WT_SESSION::verify`, metadata cursor access through `WT_METADATA_URI`, internal scratch-buffer APIs, utility URI/error helpers, and WiredTiger macros for error handling. It is a central support command for checking database integrity and inspecting page/block layout.

Risks: Dumping all data can leak application content; the code explicitly prevents combining all-data and key-only modes but each separately changes redaction. The metadata cursor is not explicitly closed here. `dump_offsets` is accepted as a raw substring inside a config list, so validation is deferred to WiredTiger config parsing. In all-table mode, unsupported objects are filtered only by prefix and `ENOTSUP` handling.

Test signals: Tests should cover each option-to-config mapping, duplicate `dump_offsets` rejection, `-u`/`-k` conflict, single-URI verification, all-table metadata iteration, abort-on-error behavior, and verbose newline output.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/utilities/util_verify.c -->
