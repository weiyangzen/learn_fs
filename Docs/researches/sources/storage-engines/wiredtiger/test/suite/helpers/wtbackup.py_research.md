<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/helpers/wtbackup.py -->
# sources/storage-engines/wiredtiger/test/suite/helpers/wtbackup.py

Purpose: Shared base class for full, selective, log, and incremental backup tests. It builds test data, copies files returned by backup cursors, applies block-range incremental copies, and compares backup homes through the `wt` utility.

Important APIs and types: `backup_base` extends `wttest.WiredTigerTestCase` and `suite_subprocess`. Key methods include `backup_get_stat`, `add_data`, `populate`, `setup_directories`, `confirmPathDoesNotExist`, `copy_file`, `take_selective_backup`, `take_full_backup`, `compare_backups`, `range_copy`, `take_incr_backup_block`, `take_log_backup`, and `take_incr_backup`.

Control flow: Tests populate objects, checkpoint when needed, open a `backup:` cursor, and iterate with `next()`/`get_key()` because backup cursors do not expose values. Full/selective backup copies complete files. Incremental backup opens a top-level cursor with `src_id`/`this_id`, then duplicate cursors with `incremental=(file=...)`; file records are copied whole and range records are copied with seek/read/write.

State and persistence behavior: The helper manages `WT_TEST_TMP`, full backup directories, incremental backup directories, optional log subdirectories, and copied WiredTiger files. It tracks backup IDs and multiplier counters to create unique data across iterations. Incremental range copies update an existing backup image in place and verify changed block content in consolidate mode.

Dependencies and integration points: Uses WiredTiger backup cursor semantics, `wiredtiger.WT_BACKUP_FILE`, `WT_BACKUP_RANGE`, connection/data-source backup statistics, `helper.compare_files`, and `suite_subprocess.runWt` for dump/verify comparisons.

Risks: Path handling assumes backup cursor keys map cleanly to local files and optional log paths. Incremental correctness depends on correct cursor ordering and stats updates. Range-copy assertions can be too strict unless consolidate mode is used because unchanged blocks may be reported separately.

Test signals: Backup cursor open/duplicate stats, range block stats, copied file lists and sizes, `wt dump` comparisons, `wt verify`, missing-URI checks, and nonzero changed-block counters validate behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/helpers/wtbackup.py -->
