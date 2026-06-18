# sources/storage-engines/wiredtiger/test/live_restore/take_backup.py

Purpose: utility script for creating a physical backup of a wtperf-generated database to use as the source directory in live restore performance tests.

Important APIs and functions: `main` assumes home `WT_TEST_0_0` and backup directory `WT_TEST_0_0_backup`. It removes any previous backup directory, creates a new one, opens WiredTiger through the Python binding, opens a `backup:` cursor, iterates backup file names, and copies each from home to backup with `shutil.copyfile`.

Control flow and state: the script is intended to run from `build/bench/wtperf` after the `btree-500m-populate` workload has produced `WT_TEST_0_0`. It mutates the local filesystem by deleting/recreating the backup directory. WiredTiger session, cursor, and connection are closed explicitly.

Dependencies and integration: appends `../../lang/python` to `sys.path`, imports `wiredtiger_open`, and uses standard `os`, `shutil`, and `sys`. It integrates with live restore perf tests outside the core CMake test flow.

Risks and test signals: the hard-coded home and destructive backup directory removal make the working directory contract important. It copies only files listed by the backup cursor, which is correct for WiredTiger backup but assumes paths are simple children of the home. Successful completion creates a full backup directory with no explicit verification beyond copy errors.
