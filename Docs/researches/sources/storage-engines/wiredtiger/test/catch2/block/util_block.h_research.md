<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/block/util_block.h -->
# sources/storage-engines/wiredtiger/test/catch2/block/util_block.h

Purpose: Declarations for shared block manager Catch2 helpers.

Important APIs/types/functions: Declares extent/size validation/free helpers, `create_write_buffer`, `setup_bm`, and `test_and_validate_write_size`.

Control flow: Header-only declarations; implementation lives in `util_block.cpp`.

State and persistence behavior: No state directly, but APIs expose mutating helper contracts for `WT_BM`, `WT_ITEM`, session block-manager caches, and test files.

Dependencies and integration points: Included by block API and unit tests; includes `wt_internal.h` and `mock_session.h`.

Risks and test signals: Signature changes affect many block tests. Build failures in `catch2-unittests` are the primary signal.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/block/util_block.h -->
