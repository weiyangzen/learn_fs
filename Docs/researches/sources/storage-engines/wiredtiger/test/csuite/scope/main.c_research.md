# sources/storage-engines/wiredtiger/test/csuite/scope/main.c

Purpose: this test verifies WiredTiger cursor key/value scope rules. It checks when an application may overwrite buffers after cursor operations and whether `get_key` and `get_value` return copied library-owned data or correct errors after insert, modify, search, search-near, reserve, update, and remove variants.

Important APIs, types, and functions: it uses `WT_EVENT_HANDLER` to suppress expected "requires key/value be set" messages, `WT_CURSOR`, `WT_SESSION`, `WT_MODIFY`, `WT_ITEM`, and helper macros `SET_KEY` and `SET_VALUE`. `cursor_scope_ops` is the main behavioral matrix. `run` creates a data source and applies the matrix. `main` opens WiredTiger and runs the matrix for file and table URIs with string keys, recno keys, string values, and raw byte values.

Control flow: each operation case creates a clean key/value record if needed, begins a snapshot transaction, opens a fresh cursor, sets application key/value buffers, performs the operation, overwrites the original buffers with marker bytes, then probes cursor state. Insert and key-based remove are expected not to position the cursor; positioned remove should preserve the key but not value; modify, reserve, search, search-near, and update should preserve both key and value through library-owned memory. Operations that intentionally create cursor state errors roll back the transaction; others commit.

State and persistence behavior: the database is temporary and created under `opts->home`. There is no crash or recovery phase. The persistent state is only the records created and removed in each data source; the real focus is transient cursor state and memory ownership after API calls.

Dependencies and integration points: this is a standalone csuite test using common `testutil_parse_opts`, `testutil_recreate_dir`, and `testutil_cleanup`. It exercises both `file:` and `table:` data sources and both row-store and column-store key formats.

Risks and test signals: the most important risk is accidental retention of application memory pointers after operations, which could become use-after-modify bugs in callers. Passing requires all `testutil_assert` checks and expected error filtering to complete. Any unexpected error message is printed with `session->strerror`.
