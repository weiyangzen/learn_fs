# sources/storage-engines/wiredtiger/test/suite/test_bug029.py

Purpose: regression for WT-9457, verifying that the most recent checkpoint time propagates across restarts so a backup cursor cannot lose its pinned checkpoint.

Important APIs/types/functions: `session.checkpoint(force=1)`, backup cursor `open_cursor('backup:')`, `shutil.copy`, `wiredtiger_open`, `reopen_conn`, and helper `add_data`.

Control flow: populate 2,000 rows and checkpoint, force 100 quick checkpoints, add 2,000 more rows and checkpoint, reopen, modify some rows, open a backup cursor, force 10 checkpoints, add/checkpoint more data to encourage block reuse, copy files listed by the backup cursor into `backup_dir`, open the backup, and sample-read keys every 10 rows from 0 to 3990.

State/persistence behavior: stresses checkpoint deletion and block reuse while a backup cursor pins an older checkpoint after restart. The pinned checkpoint must remain valid for backup restore.

Dependencies/integration: checkpoint metadata timing, backup cursor, filesystem copy, restart behavior, and table reads from the backup home.

Risks/test signals: potential failure is fatal read/panic or wrong sampled values in backup. Uses real backup file copying rather than only metadata inspection.
