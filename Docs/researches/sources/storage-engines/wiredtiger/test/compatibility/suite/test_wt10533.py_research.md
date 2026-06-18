# sources/storage-engines/wiredtiger/test/compatibility/suite/test_wt10533.py

Purpose: Regression test for checkpoint handling during downgrade when many checkpoints force monotonic checkpoint time far ahead of wallclock time.

Important APIs/types/functions: `test_checkpoint_downgrade` runs a newer-branch phase followed by an older-branch phase. `on_newer_branch_test_checkpoint_downgrade` creates a table, writes initial rows, and creates many checkpoints. `on_older_branch_test_checkpoint_downgrade` opens with compatibility/statistics config, starts a backup cursor, writes large batches across more checkpoints, copies backup files, reopens the backup, and verifies initial rows.

Control flow: newer branch creates the starting database and checkpoint history; older branch continues writing and checkpointing while a backup cursor is active, materializes a backup, and validates backup readability.

State and persistence: persists the database home, checkpoint metadata, statistics logs, backup directory, copied WiredTiger files, and table contents across branch-specific subprocesses.

Dependencies/integration: uses `CompatibilityTestCase`, Python `wiredtiger`, filesystem `os/shutil`, captured test output, and branch scenario generation.

Risks and test signals: large row/checkpoint counts make the test expensive but targeted. Backup copying assumes files returned by `backup:` are copyable by name from the current home. Data verification of the original rows is the final compatibility signal.
