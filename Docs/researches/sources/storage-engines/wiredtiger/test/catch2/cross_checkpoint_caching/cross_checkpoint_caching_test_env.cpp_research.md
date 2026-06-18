<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/cross_checkpoint_caching/cross_checkpoint_caching_test_env.cpp -->
# sources/storage-engines/wiredtiger/test/catch2/cross_checkpoint_caching/cross_checkpoint_caching_test_env.cpp

Purpose: Implements a real WiredTiger environment for cross-checkpoint shared disk cache tests.

Important APIs/types/functions: Constructor opens `DB_HOME`, creates a table, opens a cursor, borrows the cursor dhandle, installs a dummy disaggregated page-log handle, initializes shared disk cache, and marks it active. Destructor destroys cache, clears state, closes cursor, clears dhandle, and drops table. Methods expose `session`, `stats`, `btree_id`, `put`, and `bucket_size`.

Control flow: `put` allocates page-sized data, initializes `WT_PAGE_BLOCK_META`, calls `__wt_shared_dsk_cache_put`, frees duplicate data on collision, and returns the cache item.

State and persistence behavior: Creates/drops `table:cross_checkpoint_caching_test` in `DB_HOME`, mutates connection cache state and disaggregated-storage sentinel.

Dependencies and integration points: Used by get/put/release tests; depends on `connection_wrapper`, WiredTiger cache internals, and Catch2 assertions.

Risks and test signals: Borrowed dhandle and dummy disagg sentinel are delicate. Signals include destructor cleanup, no lingering table, correct active/off cache state, and bucket-count correctness.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/cross_checkpoint_caching/cross_checkpoint_caching_test_env.cpp -->
