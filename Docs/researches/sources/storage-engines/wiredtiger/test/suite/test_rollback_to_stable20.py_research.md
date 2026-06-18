# sources/storage-engines/wiredtiger/test/suite/test_rollback_to_stable20.py

Purpose: regression test for dhandle cleanup during recovery-time RTS. It creates many tables so recovery must open and close many data handles without leaking them.

Important APIs/types/functions: extends the RTS base; uses `SimpleDataSet`, timestamped updates, `conn.set_timestamp`, `session.checkpoint`, `simulate_crash_restart`, and `stat.conn.dh_conn_handle_count`.

Control flow: creates many tables with identical data and timestamped updates, pins oldest/stable around the update time, checkpoints, simulates crash/restart, then reads the connection handle count statistic.

State and persistence behavior: the core state is metadata/dhandle lifecycle rather than row visibility. Recovery RTS scans many objects and should not leave all handles open after restart.

Dependencies and integration points: integrates with WiredTiger dhandle manager, metadata scan during RTS, and recovery simulation. It also uses the common dataset and scenario machinery.

Risks: handle-count thresholds can be sensitive to unrelated open metadata objects. The test uses a low expected count to catch leaks but not exact equality.

Test signals: asserts `open_dhandle_count < 5` after restart, showing RTS did not pin one handle per tested table.
