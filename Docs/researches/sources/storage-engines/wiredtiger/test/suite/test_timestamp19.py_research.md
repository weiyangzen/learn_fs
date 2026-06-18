<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_timestamp19.py -->
# sources/storage-engines/wiredtiger/test/suite/test_timestamp19.py

Purpose: Ensures the oldest timestamp persisted in metadata is restored as the connection's oldest timestamp after restart.

Important APIs/types/functions: `test_timestamp19` uses `SimpleDataSet`, `updates()`, `conn.set_timestamp`, `session.checkpoint('use_timestamp=true')`, `close_conn`, `setUpConnectionOpen`, and `query_timestamp`.

Control flow: The test sets oldest/stable to 10, writes batches at 20, 30, and 40, checkpoints, advances oldest/stable to 40, writes more batches at 50, 60, and 70, checkpoints again, and reopens the connection. It then verifies setting oldest back to 10 fails and that oldest is recovered as 40, before advancing both oldest and stable to 70.

State and persistence behavior: The key state is metadata persisted by timestamped checkpoints. Restart recovery must seed the in-memory oldest timestamp from metadata, preventing illegal rollback of oldest.

Dependencies and integration points: Exercises metadata recovery, timestamp validation, checkpoint timestamping, and restart path in the WiredTiger test harness.

Risks: If metadata recovery loses oldest, applications could set oldest too far back after restart, invalidating history-store cleanup assumptions.

Test signals: The expected `WiredTigerError` message for setting oldest to 10 and exact query checks for 40 and 70 are the main pass/fail signals.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_timestamp19.py -->
