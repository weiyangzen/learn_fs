# sources/sync-backup/rsync/testsuite/backup-deep_test.py

Purpose: property-level depth coverage for `--backup`, custom suffixes, `--backup-dir` outside the destination tree, and deletion capture under backup-dir.

Important APIs/types/functions: `make_tree`, `walk_files`, `run_rsync`, `assert_same`, `assert_not_exists`, `test_fail`, and sibling backup path `SCRATCHDIR/backups`.

Control flow: `seed()` creates a v1 source, copies it to destination, records old bytes, then mutates source to v2. The test verifies same-directory suffix backups contain v1, external backup-dir preserves deep relative paths with v1 bytes, and `--backup-dir --delete` moves a deep extraneous destination file into the backup tree.

State and persistence behavior: compares old content, new destination content, and backup-tree placement. The backup directory is outside both source and destination to exercise cross-directory rename/copy behavior.

Dependencies and integration points: rsync backup receiver logic, delete handling, no-whole-file updates, and harness content assertions.

Risks and test signals: failures show missing backups, wrong saved content, path flattening, or deletion loss at depth.
