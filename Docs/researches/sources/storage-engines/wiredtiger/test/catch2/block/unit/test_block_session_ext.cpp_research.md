<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/block/unit/test_block_session_ext.cpp -->
# sources/storage-engines/wiredtiger/test/catch2/block/unit/test_block_session_ext.cpp

Purpose: Tests extent-node allocation, preallocation, cache reuse, free, and discard behavior in block manager sessions.

Important APIs/types/functions: Exercises `__ut_block_ext_alloc`, `__ut_block_ext_prealloc`, `__wti_block_ext_alloc`, `__wti_block_ext_free`, and `__ut_block_ext_discard`.

Control flow: Sections allocate directly, preallocate different cache sizes, allocate from null manager sessions, pop cached extents, clear junk `next` pointers, push frees onto cache, and discard to a maximum count.

State and persistence behavior: Mutates `WT_BLOCK_MGR_SESSION::ext_cache`, `ext_cache_cnt`, and `WT_EXT::next` chains.

Dependencies and integration points: Uses `mock_session` and shared extent validators; covers block extent cache internals.

Risks and test signals: Cache count underflow, stale next pointers, and inconsistent counts are primary risks. Signals include expected cache list length and `WT_ERROR` on fake over-count discard.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/block/unit/test_block_session_ext.cpp -->
