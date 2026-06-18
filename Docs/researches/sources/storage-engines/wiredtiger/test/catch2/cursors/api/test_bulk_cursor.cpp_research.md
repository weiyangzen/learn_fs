<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/cursors/api/test_bulk_cursor.cpp -->
# sources/storage-engines/wiredtiger/test/catch2/cursors/api/test_bulk_cursor.cpp

Purpose: Tests cursor, bulk cursor, checkpoint, drop, transaction, and cache-destroy interactions.

Important APIs/types/functions: Helpers insert raw key/value pairs, run checkpoint/drop in threads, print diagnostics, check transaction modifications, report cache status, and drive `cache_destroy_memory_check`, `cursor_test`, and `multiple_drop_test`.

Control flow: Opens connections and sessions, creates `table:cursor_test`, begins transactions, opens regular or bulk cursors, inserts sample values where allowed, attempts checkpoints/drops in same or second thread, and commits or rolls back with expected results.

State and persistence behavior: Creates/drops tables in `DB_HOME`, mutates transactions, dhandles, cache counters, and cursor lifecycle state.

Dependencies and integration points: Uses public WiredTiger API, internal cursor raw setters, wrappers, item wrappers, and `std::thread`.

Risks and test signals: Threading uses the same session pointer, which targets specific contention behavior. Several non-bulk variants are commented out. Signals are expected `EINVAL`, `EBUSY`, successful rollback/commit, and repeated force-drop stability.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/cursors/api/test_bulk_cursor.cpp -->
