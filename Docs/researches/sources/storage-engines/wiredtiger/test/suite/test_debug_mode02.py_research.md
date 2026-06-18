# sources/storage-engines/wiredtiger/test/suite/test_debug_mode02.py

Purpose: tests `debug_mode=(checkpoint_retention=N)` interaction with log file removal and reconfiguration.

Important APIs and control flow: connection config enables logging with `file_max=100K` and checkpoint retention. `advance_log_checkpoint` writes enough data to roll to a new log file, then checkpoints. `check_remove` polls for a named log file to disappear. `test_checkpoint_retain` confirms log sets grow as a superset until retention is exceeded, then the first log is removed.

State and persistence: the test inspects real `WiredTigerLog.*` files under the test home. Checkpoints and log archival are the persistence behavior under test.

Dependencies and integration: uses `suite_subprocess`, filesystem `os.listdir`, `fnmatch`, `time.sleep`, `wiredtiger.WiredTigerError`, and `conn.reconfigure`.

Risks and test signals: timing is inherently asynchronous, so removal polling runs up to 90 seconds. Reconfiguration checks include allowed same-value toggles and a prohibited change to another nonzero retention value.
