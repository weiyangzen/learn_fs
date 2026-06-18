# sources/sync-backup/rsync/testsuite/backup_test.py

Purpose: ported regression coverage for `--backup`, `--backup-dir`, `--delete-delay`, and `--backup --inplace` behavior on changed files.

Important APIs/types/functions: `_cat_glob`, `_run_and_capture`, `checkit`, `verify_dirs`, `cp_touch`, `rsync_argv`, `diff`, and backup info output checks.

Control flow: build two source files from source-code glob concatenations, establish destination and check copies, mutate source, then run plain backup and verify `name~` output and content. Next add a destination-only file and run backup-dir with delete-delay, verifying backup messages and backup-dir contents. Finally reset check state, mutate again, run inplace backup-dir, verify destination and backup tree, then sync bakdir cleanly.

State and persistence behavior: uses `CHKDIR` as the pre-rsync content oracle and `TMPDIR/bak` as backup storage. It moves same-directory backups back into place before the next phase.

Dependencies and integration points: backup itemization, delta transfer, delete-delay, backup-dir pathing, inplace updates, and external `diff`.

Risks and test signals: relies on backup info text fragments. Failures mean backup output or saved-content semantics changed.
