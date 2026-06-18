<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_truncate09.py -->
# sources/storage-engines/wiredtiger/test/suite/test_truncate09.py

Purpose: Tests rollback-to-stable behavior for fast-truncated ranges and single-row removes after crash restart.

Important APIs/types/functions: `test_truncate09` uses `simulate_crash_restart`, `session.truncate`, timestamped commits, oldest/stable timestamp setting, checkpoints, `simple_key`, and `simple_value`. It skips disaggregated storage because RTS is unsupported there.

Control flow: The test populates 80,000 rows, reopens, sets oldest/stable to 100, truncates keys 20,000-40,000 at timestamp 150, advances stable to 200 and checkpoints, then truncates 50,000-70,000 and removes key 75,000 at timestamp 250 without stabilizing them. After checkpoint and crash restart, it expects the stabilized truncate to remain deleted but the unstable truncate and remove to be rolled back.

State and persistence behavior: Combines on-disk fast-delete metadata, stable timestamp advancement, checkpointed unstable changes, and recovery-time rollback-to-stable.

Dependencies and integration points: Integrates checkpoint, crash restart, RTS, fast-delete, and row/column formats.

Risks: RTS must distinguish stable and unstable deleted-page metadata. Incorrect handling can either resurrect stable deletes or retain unstable deletes/removes.

Test signals: Searches after restart: key 30,000 not found, key 60,000 found, and key 75,000 found.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_truncate09.py -->
