<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/block/unit/test_extent_list_insert_wo_block.cpp -->
# sources/storage-engines/wiredtiger/test/catch2/block/unit/test_extent_list_insert_wo_block.cpp

Purpose: Tests extent insertion helpers that do not require a `WT_BLOCK`.

Important APIs/types/functions: Calls `__ut_block_ext_insert` with preallocated `WT_EXT` and `__ut_block_off_insert` with offset/size pairs.

Control flow: Inserts into empty lists and then inserts out-of-order extents, verifying sorted offset order after each insert.

State and persistence behavior: Mutates local `WT_EXTLIST` skiplist, bytes, and entries; frees through `extlist_free`.

Dependencies and integration points: Uses mock sessions, `alloc_new_ext`, and `verify_off_extent_list`; supports the lower layer used by merge/remove tests.

Risks and test signals: Ordering and skiplist pointer maintenance are key. Sections include `BREAK`, so automated test runs should verify macro configuration.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/block/unit/test_extent_list_insert_wo_block.cpp -->
