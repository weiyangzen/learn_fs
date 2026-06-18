<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/block/api/test_block_api_misc.cpp -->
# sources/storage-engines/wiredtiger/test/catch2/block/api/test_block_api_misc.cpp

Purpose: Catch2 tests for miscellaneous block manager API methods: address validation/stringification, header size, map status, size, and statistics.

Important APIs/types/functions: Helpers `check_bm_stats`, `test_addr_invalid`, and `test_addr_string` exercise `WT_BM::stat`, `addr_invalid`, and `addr_string`. Tests call `__wti_bm_method_set`, `setup_bm`, `__wt_block_addr_pack`, `bm.write`, `bm.size`, and `__wt_block_close`.

Control flow: Each section opens or initializes a `WT_BM`, packs synthetic address cookies, invokes the relevant block-manager API, checks derived values, and closes/drops the backing file where needed.

State and persistence behavior: Creates `test.wt` in the current working directory and updates live block statistics and extent-list state through actual block-manager setup.

Dependencies and integration points: Depends on block test helpers, mock sessions, WiredTiger block internals, filesystem paths, and extent utilities.

Risks and test signals: Tests know address cookie internals and include a disabled panic scenario. Important signals are stats consistency after writes, zero-size address handling, and filesystem cleanup.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/block/api/test_block_api_misc.cpp -->
