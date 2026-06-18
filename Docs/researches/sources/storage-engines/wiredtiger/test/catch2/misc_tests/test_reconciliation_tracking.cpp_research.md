# Research: sources/storage-engines/wiredtiger/test/catch2/misc_tests/test_reconciliation_tracking.cpp

## sources/storage-engines/wiredtiger/test/catch2/misc_tests/test_reconciliation_tracking.cpp

Purpose: Catch2 regression tests for reconciliation overflow tracking internals. The file reaches into `src/reconcile/reconcile_private.h` and `reconcile_inline.h` through unit-test entry points such as `__ut_ovfl_track_init`, `__ut_ovfl_discard_verbose`, `__ut_ovfl_discard_wrapup`, `__ut_ovfl_reuse_wrapup`, `__ut_ovfl_reuse_wrapup_err`, plus production helper `__wti_ovfl_reuse_add`.

Important setup: `connection_wrapper` opens a real WiredTiger home so allocation/free paths run against a real session. `block_free_fail` and `setup_failing_bm` install a minimal `WT_BM` whose `free` method returns `EINVAL`, wiring it through `WT_BTREE`, `WT_DATA_HANDLE`, and `session->dhandle`.

Control flow: tests allocate zeroed `WT_PAGE` and `WT_PAGE_MODIFY`, initialize overflow tracking, exercise empty discard wrapup, then add an overflow reuse entry and force wrapup through the block-free failure branch. They clear `WT_OVFL_REUSE_INUSE` and `WT_OVFL_REUSE_JUST_ADDED` flags to make the entry eligible for reuse wrapup.

State and persistence: this is in-memory reconciliation state only. The key state is `page.modify->ovfl_track`, `page.memory_footprint`, and the session dhandle's block manager. Tests assert failed block frees restore memory footprint to zero and propagate `EINVAL`.

Dependencies/integration: depends on real WiredTiger connection lifecycle, internal reconciliation headers, block manager function pointers, `__wt_ovfl_reuse_free`, and `__wt_free`. Risks are high coupling to private layout and UT wrapper names. Test signals are direct `REQUIRE` checks for allocation, error propagation, and cleanup invariants.

<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/catch2/misc_tests/test_reconciliation_tracking.cpp -->
