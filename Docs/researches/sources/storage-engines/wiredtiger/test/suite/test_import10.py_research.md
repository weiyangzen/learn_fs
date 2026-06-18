# sources/storage-engines/wiredtiger/test/suite/test_import10.py

Purpose: validates import/export interaction while a backup cursor is open. Imported files should not be included in the in-progress backup file list.

Important APIs and functions: `test_import10` extends `wtbackup.backup_base`. Scenarios cover import with metadata and repair import. `get_stat` reads `session_table_create_import_success` and `session_table_create_import_repair`.

Control flow: the test creates and populates `table:test_import10`, checkpoints, exports table/file metadata, drops the table with `remove_files=false`, verifies opening it fails, opens a `backup:` cursor, imports the table using the scenario config, checks import statistics, verifies and reads all rows, then performs a full backup using the still-open backup cursor and asserts the imported file is absent from the backup file set.

State and persistence behavior: the backup cursor captures a backup view before import. The imported file should not retroactively enter that view even though it exists by the time backup files are copied.

Dependencies and integration points: integrates backup cursor semantics, table import, drop-with-retained-files, import stats, and `take_full_backup`.

Risks and edge cases: relies on backup cursor snapshot semantics and file naming. It checks integer data only, not timestamped import.

Test signals: import success stat equals 1; repair stat matches scenario; all rows read correctly; `test_import10.wt` is not in the full backup file list.
