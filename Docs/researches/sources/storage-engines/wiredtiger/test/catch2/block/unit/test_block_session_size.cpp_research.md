<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/block/unit/test_block_session_size.cpp -->
# sources/storage-engines/wiredtiger/test/catch2/block/unit/test_block_session_size.cpp

Purpose: Tests size-node allocation, preallocation, cache reuse, free, and discard behavior for block manager sessions.

Important APIs/types/functions: Calls `__ut_block_size_alloc`, `__ut_block_size_prealloc`, `__wti_block_size_alloc`, `__wti_block_size_free`, and `__ut_block_size_discard`.

Control flow: Mirrors extent-cache tests for `WT_SIZE`: allocate empty nodes, grow cache to requested size, reuse cached nodes even with zero count or junk links, push freed nodes, and discard down to target maximums.

State and persistence behavior: Mutates `WT_BLOCK_MGR_SESSION::sz_cache`, `sz_cache_cnt`, and `WT_SIZE::next`.

Dependencies and integration points: Uses `wt_internal.h`, mock sessions, and shared size validators; protects block free-space size skiplist cache.

Risks and test signals: Incorrect cache counts or stale links can lead to leaks or corrupted freelists. Test signal is exact cache length and `WT_ERROR` for fake count mismatch.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/block/unit/test_block_session_size.cpp -->
