<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/block/unit/test_extent_list_insert_block.cpp -->
# sources/storage-engines/wiredtiger/test/catch2/block/unit/test_extent_list_insert_block.cpp

Purpose: Tests block-aware extent-list merge, remove, append, and file-size extension helpers.

Important APIs/types/functions: Calls `__ut_block_merge`, `__ut_block_off_remove`, `__ut_block_append`, and `__ut_block_extend`; uses `off_size_expected`, `off_expected`, and `block_append_test` fixtures.

Control flow: Sections insert/merge adjacent extents, remove by offset with optional returned node, append adjacent/non-adjacent extents, and extend block size including invalid/overflow cases.

State and persistence behavior: Mutates local `WT_EXTLIST` entries/bytes/last and local `WT_BLOCK::size`; no real file extension.

Dependencies and integration points: Uses mock sessions, `utils_extlist`, and block internals. Several sections start with `BREAK`, so harness macro behavior determines whether they run normally.

Risks and test signals: Adjacent coalescing and overflow are the main risks. `BREAK` markers are a test-execution risk; CI should confirm these sections are not unexpectedly trapping.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/block/unit/test_extent_list_insert_block.cpp -->
