<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/cross_checkpoint_caching/unit/test_cross_checkpoint_caching_get.cpp -->
# sources/storage-engines/wiredtiger/test/catch2/cross_checkpoint_caching/unit/test_cross_checkpoint_caching_get.cpp

Purpose: Tests shared disk cache lookup behavior across address, address-size, file-id, and hash-collision cases.

Important APIs/types/functions: Uses `cross_checkpoint_caching_test_env::put`, `bucket_size`, `stats`, `btree_id`, and direct `__wt_shared_dsk_cache_get`.

Control flow: Tests miss on empty cache, hit increments `ref_count`, different address/size/file id misses, repeated hits accumulate stats/refcounts, forced same-bucket collisions distinguish by address, and same address with different file ids resolves by current btree id.

State and persistence behavior: Mutates cache hash buckets, item `ref_count`, connection stats, and temporarily changes `S2BT(session)->id`.

Dependencies and integration points: Integrates with real WiredTiger connection fixture and shared disk cache internals.

Risks and test signals: Direct btree id mutation must be restored. Signals are hit/miss stat counters, nulling of miss output, and exact item identity under collisions.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/cross_checkpoint_caching/unit/test_cross_checkpoint_caching_get.cpp -->
