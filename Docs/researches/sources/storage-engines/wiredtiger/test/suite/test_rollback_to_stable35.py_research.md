# sources/storage-engines/wiredtiger/test/suite/test_rollback_to_stable35.py

Purpose: reproduces a checkpoint/logging race by copying the WiredTiger home while a checkpoint is stopped under timing stress, then opening the copied home and checking that RTS/recovery does not do unexpected work.

Important APIs/types/functions: extends RTS base; defines local two-table `large_updates` and `check`. Uses `checkpoint_thread`, `copy_wiredtiger_home`, `threading.Event`, checkpoint stop timing-stress statistics, logging with `force_write_wait`, and RTS statistics.

Control flow: creates two tables, writes baseline data, opens a long-running transaction, writes more data, starts a checkpoint thread and waits for checkpoint activity, writes additional data, evicts, waits for checkpoint stop timing stress, copies the home to `RESTART`, completes checkpoint/transaction cleanup, opens the copied home, and verifies latest data.

State and persistence behavior: the copied home represents a checkpoint race snapshot. The test expects recovery to preserve the latest copied state without invoking meaningful RTS work, reflected by zero calls/pages/aborts and nonnegative history-store removal.

Dependencies and integration points: integrates logging, checkpoint timing stress, home copying, two-table consistency, and recovery open path.

Risks: highly timing-sensitive; relies on timing-stress hooks and checkpoint state stats. It can be slow or flaky if checkpoint stop is not reached.

Test signals: two-table value checks after opening the copied home and stats asserting `calls == 0`, `keys_removed == 0`, `keys_restored == 0`, `pages_visited == 0`, `upd_aborted == 0`.
