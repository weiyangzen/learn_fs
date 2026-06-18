<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/block/unit/test_block_session_bms.cpp -->
# sources/storage-engines/wiredtiger/test/catch2/block/unit/test_block_session_bms.cpp

Purpose: Tests block manager session allocation, preallocation, and cleanup across combined extent and size caches.

Important APIs/types/functions: Calls `__wti_block_ext_prealloc` and unit wrapper `__ut_block_manager_session_cleanup`; validates with `validate_ext_list` and `validate_size_list`.

Control flow: Tests allocate a block manager session when absent, grow existing caches, clean up null and non-null sessions, and inject fake cache counts to force `WT_ERROR`.

State and persistence behavior: Mutates `WT_SESSION_IMPL::block_manager`, `WT_BLOCK_MGR_SESSION::ext_cache_cnt`, and `sz_cache_cnt`.

Dependencies and integration points: Uses mock sessions and block helper validation. Exercises per-session block manager cache ownership.

Risks and test signals: Manual freeing and fake count injection can expose ownership bugs. Signals are correct nulling of `session_impl->block_manager` and error return on inconsistent cache counts.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/block/unit/test_block_session_bms.cpp -->
