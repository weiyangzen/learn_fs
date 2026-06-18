<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/cursors/unit/test_cursor_get_raw_key_value.cpp -->
# sources/storage-engines/wiredtiger/test/catch2/cursors/unit/test_cursor_get_raw_key_value.cpp

Purpose: Tests `WT_CURSOR::get_raw_key_value` against normal cursor key/value retrieval and unsupported cursor types.

Important APIs/types/functions: Helpers initialize `WT_ITEM`, insert raw key/value pairs with `__wt_cursor_set_raw_key/value`, validate `get_key`/`get_value`, and validate `get_raw_key_value` with optional null key/value output pointers.

Control flow: Creates `table:cursor_test`, inserts five records, iterates with standard getters, iterates with raw getter including key-only/value-only calls, and opens a dump-version cursor on the underlying file to expect `ENOTSUP`.

State and persistence behavior: Creates table/file in `DB_HOME`, opens/closes cursors and session.

Dependencies and integration points: Uses WiredTiger public API plus internal raw cursor helpers and wrappers.

Risks and test signals: Raw `WT_ITEM` data is compared as C strings, so formats must remain string-compatible. Signals include ordered iteration, `WT_NOTFOUND` at end, null pointer handling, and unsupported version cursor error.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/cursors/unit/test_cursor_get_raw_key_value.cpp -->
