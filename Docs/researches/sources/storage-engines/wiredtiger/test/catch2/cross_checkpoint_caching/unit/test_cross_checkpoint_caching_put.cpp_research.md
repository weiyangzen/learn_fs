<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/cross_checkpoint_caching/unit/test_cross_checkpoint_caching_put.cpp -->
# sources/storage-engines/wiredtiger/test/catch2/cross_checkpoint_caching/unit/test_cross_checkpoint_caching_put.cpp

Purpose: Tests insertion and collision semantics for cross-checkpoint shared disk cache entries.

Important APIs/types/functions: Uses fixture `put`, `bucket_size`, `__wt_shared_dsk_cache_get`, and manual `S2BT(session)->id` changes.

Control flow: Inserts new items, verifies retrievability, repeats same address/file id to ensure existing item is returned with incremented `ref_count`, inserts different addresses in one bucket, and inserts same address under different file ids as distinct entries.

State and persistence behavior: Mutates shared disk cache buckets and item reference counts; changes btree id within tests.

Dependencies and integration points: Covers `__wt_shared_dsk_cache_put` behavior via fixture abstraction.

Risks and test signals: Hash-size `1` forces collisions and stresses equality checks. Signals are bucket sizes, inserted flag, item identity, fid, addr, and refcount values.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/cross_checkpoint_caching/unit/test_cross_checkpoint_caching_put.cpp -->
