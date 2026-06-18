<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_fast_truncate01.py -->
# sources/storage-engines/wiredtiger/test/suite/test_layered_fast_truncate01.py

Purpose: tests basic follower-side range truncate behavior for layered objects, across both `layered:` URIs and `table:` URIs configured with `block_manager=disagg,type=layered`.

Important APIs/types/functions: `test_layered_fast_truncate01` derives from `LayeredFastTruncateConfigMixin` and `wttest.WiredTigerTestCase`, is expanded by `@disagg_test_class` and `make_scenarios`, and uses `wiredtiger.WT_NOTFOUND`, `session.truncate`, explicit transactions, `reopen_conn`, and `disagg_get_complete_checkpoint_meta`.

Control flow: each test creates and populates 1000 string-keyed rows on a leader, checkpoints, reopens as follower at the produced checkpoint, and then exercises truncate. `test_truncate_basic` checks isolation before commit and invisibility after commit from a second session. `test_truncate_rollback` checks rollback restores visibility. `test_truncate_write_conflict_1` keeps a truncate uncommitted and verifies a concurrent update inside the range raises the expected conflict.

State and persistence behavior: the test transitions stable checkpointed data into follower mode, then verifies follower-local truncate state affects only committed visibility unless rolled back.

Dependencies/integration points: depends on WiredTiger Python test harness, disaggregated storage helpers, checkpoint metadata pickup, and the shared fast-truncate mixin. Risks are missed cleanup of cursors/sessions and scenario differences between native layered and table-layered configurations. Test signals are exact search return codes and expected conflict message text.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_fast_truncate01.py -->
