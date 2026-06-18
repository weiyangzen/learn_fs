# sources/storage-engines/wiredtiger/examples/c/ex_cursor.c

Purpose: focused cursor API example covering scans, bounds, search/search_near, insert/update/remove, projections, statistics cursors, and debug version cursors.

Important APIs and control flow: helper functions operate on a passed `WT_CURSOR`: forward and reverse scans loop to `WT_NOTFOUND`, `cursor_bound` sets a lower bound, `cursor_search` and `cursor_search_near` show positioning semantics, and mutation helpers set key/value before insert/update/remove. `version_cursor_dump` opens a debug dump-version file cursor and extracts transaction/timestamp metadata fields. `main` opens a connection with fast stats, creates a projected `table:world`, opens table/projection/statistics cursors, then creates `table:map` and runs mutation and scan helpers before opening `file:map.wt` with `debug=(dump_version=(enabled=true))`.

State and persistence: creates `world` and `map` tables, inserts/removes/reinserts `foo`, and reads version metadata from the backing file. Cursor reset/positioning state is explicit between operations.

Dependencies and integration: depends on WiredTiger cursor ABI and debug cursor support. Uses `test_util.h` for setup and error handling.

Risks: version cursor field order is tightly coupled to WiredTiger debug cursor value format. `cursor_bound` is declared but not used in `main`, so bound behavior is compile-checked only if externally referenced.

Test signals: successful helper calls, scan termination at `WT_NOTFOUND`, and valid version cursor unpacking show cursor API compatibility.
