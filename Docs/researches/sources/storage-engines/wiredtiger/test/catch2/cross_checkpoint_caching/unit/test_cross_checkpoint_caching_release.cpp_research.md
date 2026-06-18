<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/cross_checkpoint_caching/unit/test_cross_checkpoint_caching_release.cpp -->
# sources/storage-engines/wiredtiger/test/catch2/cross_checkpoint_caching/unit/test_cross_checkpoint_caching_release.cpp

Purpose: Tests release and eviction semantics for shared disk cache items.

Important APIs/types/functions: Calls `__wt_shared_dsk_cache_release` and `__wt_shared_dsk_cache_get` through the cross-checkpoint fixture.

Control flow: Releases items with `ref_count > 1`, verifies zero refcount removes entries, ensures releasing one item in a collision bucket leaves others, balances repeated gets with releases, and tests same-address/different-file-id removal.

State and persistence behavior: Mutates item `ref_count`, bucket membership, hit/miss stats, and temporary btree ids.

Dependencies and integration points: Exercises shared disk cache lifecycle against real connection/cache state.

Risks and test signals: Use-after-free is avoided by inspecting buckets after final release rather than dereferencing freed item. Signals include bucket size, null miss output, surviving item identity, and refcount countdown.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/cross_checkpoint_caching/unit/test_cross_checkpoint_caching_release.cpp -->
