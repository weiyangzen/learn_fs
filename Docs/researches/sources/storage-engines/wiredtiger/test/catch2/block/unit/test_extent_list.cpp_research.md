<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/block/unit/test_extent_list.cpp -->
# sources/storage-engines/wiredtiger/test/catch2/block/unit/test_extent_list.cpp

Purpose: Tests extent and size skiplist search primitives used by block free-space management.

Important APIs/types/functions: Local wrappers allocate raw `WT_EXT`/`WT_SIZE` nodes. Tests call `__ut_block_off_srch_last`, `__ut_block_off_srch`, `__ut_block_first_srch`, and `__ut_block_size_srch`.

Control flow: Builds empty, single-entry, and three-entry skiplist layouts, invokes search helpers, and verifies returned stack pointers or first-fit status.

State and persistence behavior: Local heap-allocated wrappers only; no WiredTiger file state.

Dependencies and integration points: Uses `utils_extlist` validation and mock sessions for first-fit search. These helpers underpin extent insert/remove/merge behavior.

Risks and test signals: Pointer-to-pointer stack correctness is subtle, especially with alternate skip offsets. Signals include exact stack locations for empty, exact-match, after-maximum, and skip-offset searches.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/block/unit/test_extent_list.cpp -->
