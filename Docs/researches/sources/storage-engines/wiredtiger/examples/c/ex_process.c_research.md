# sources/storage-engines/wiredtiger/examples/c/ex_process.c

Purpose: minimal example for opening WiredTiger in multi-process mode.

Important APIs and control flow: `main` uses `example_setup`, opens a connection with `wiredtiger_open(home, NULL, "create,multiprocess", &conn)`, opens one session, does placeholder work, and closes the connection.

State and persistence: creates a WT_HOME configured for multi-process access. No table data is created by the example.

Dependencies and integration: depends on WiredTiger's `multiprocess` connection configuration and `test_util.h`.

Risks: it does not actually spawn multiple processes or demonstrate coordination, locking, or workload isolation. It validates the configuration path, not concurrent behavior.

Test signals: successful open/session/close with `multiprocess` enabled. Deeper validation would require independent processes sharing the same home.
