# sources/storage-engines/wiredtiger/examples/c/ex_backup.c

Purpose: integration example for full and block-based incremental backup with logging enabled.

Important APIs and control flow: global constants define the source home, backup homes, log path, output dumps, table URIs, and ID range. `setup_directories` prepares full and incremental backup directories. `add_work` inserts batches into `table:main` and, on even iterations, `table:extra`. `take_full_backup` opens `backup:` with either full or initial incremental configuration, copies listed files, and tracks file lists. `take_incr_backup` queries existing IDs via `backup:query_id`, opens `backup:` with `incremental=(src_id,this_id[,consolidate])`, duplicates the cursor per file with `incremental=(file=...)`, and applies whole-file or range copies using `open`, `lseek`, `read`, and `write`. `compare_backups` shells out to `../../wt -R ... dump main` and `cmp`.

State and persistence: creates WT_BLOCK, per-iteration full/incremental homes, log directories, dump outputs, persistent incremental backup ID metadata, and file-list memory state. It verifies ID persistence across close/reopen and then uses `force_stop=true` to remove incremental metadata.

Dependencies and integration: requires POSIX shell utilities and file APIs, the copied `../../wt` binary, logging, checkpoints, and backup cursors.

Risks: path assumptions and shell commands are platform-sensitive. File list removal uses broad `rm WT_BLOCK_LOG_*` patterns. Range-copy correctness depends on offsets, sizes, and descriptor lifecycle.

Test signals: every iteration must compare full and incremental dumps as identical; final reopen must fail to open incremental backup after forced stop and `WiredTiger.backup.block` must be absent.
