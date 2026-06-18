<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/block/utils_extlist.cpp -->
# sources/storage-engines/wiredtiger/test/catch2/block/utils_extlist.cpp

Purpose: Debug, allocation, cleanup, and verification utilities for block extent-list tests.

Important APIs/types/functions: Implements `operator<` for `off_size`, printing helpers, `alloc_new_ext`, `get_off_n`, `ext_free_list`, `size_free_list`, `extlist_free`, `verify_empty_extent_list`, `verify_off_extent_list`, and stream operators for `off_size`, `WT_EXT`, and `WT_EXTLIST`.

Control flow: Allocation wraps `__wti_block_ext_alloc`; cleanup frees only top-level skiplist chains; verification iterates level 0 and compares offsets/sizes/bytes.

State and persistence behavior: Allocates and frees `WT_EXT`/`WT_SIZE` test nodes and mutates extlist heads during cleanup.

Dependencies and integration points: Used by all extent-list tests; depends on Catch2 `INFO`/`REQUIRE` and WiredTiger block allocation helpers.

Risks and test signals: Cleanup must avoid double-freeing nodes referenced by multiple skip levels. Diagnostic print helpers improve failure triage but can hide ownership mistakes if verification is incomplete.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/block/utils_extlist.cpp -->
