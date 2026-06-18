# sources/storage-engines/wiredtiger/test/suite/test_hs33.py

Purpose: regression test for recovery when many tables have history-store activity and a crash/copy occurs during a checkpoint stop timing-stress point. It protects metadata recovery from opening data files/history too early.

Important APIs and functions: `test_hs33` extends `WiredTigerTestCase` and `suite_subprocess`. Helpers `large_updates` and `add_insert` populate/update many `SimpleDataSet` tables. It uses `checkpoint_thread`, `copy_wiredtiger_home`, `timing_stress_for_test=[checkpoint_stop]`, and statistics `checkpoint_stop_stress_active`.

Control flow: the test creates 99 logged-disabled tables, inserts small records, opens a long transaction, updates every table with a larger value, reconfigures checkpoint stop timing stress, starts a checkpoint thread, waits for the stress statistic, copies the home to `RESTART`, stops the checkpoint thread, closes the original connection, then reopens `RESTART` with aggressive dirty eviction settings to trigger recovery replay paths.

State and persistence behavior: the copied home represents an incomplete checkpoint with metadata log records in flight. Recovery must complete using correct checkpoint metadata and avoid opening files before metadata recovery has selected the proper checkpoint.

Dependencies and integration points: integrates checkpoint timing stress, threading, home-copy helper, recovery, metadata logging, history-store state, and eviction.

Risks and edge cases: timing-stress polling can hang if the stat is not reached; it is concurrency-sensitive. The test does not verify all table values after restart, so its main signal is successful recovery under low cache/eviction pressure.

Test signals: opening the copied home under recovery completes without WiredTiger errors or assertions.
