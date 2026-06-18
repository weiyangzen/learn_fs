# sources/storage-engines/foundationdb/fdbbackup/tests/backup_tests_common.sh

## Purpose

`backup_tests_common.sh` is the shared shell harness for backup/restore integration tests. It abstracts command-argument construction, S3/MockS3 cleanup, backup submission and polling, restore submission and polling, encryption mismatch assertions, and common cluster setup.

## Important APIs, Types, and Functions

`add_base_args` appends cluster-file and trace-log flags, choosing `-C` for backup commands and `--dest-cluster-file` for restore commands. `add_common_optional_args` appends blob credentials, `--mode`, encryption key file, and global `KNOBS`. `s3_preclear_url` and `s3_cleanup_url` wrap `s3client rm` with provider-specific TLS behavior. `run_backup` starts `fdbbackup start`, polls `fdbbackup status` until the backup is restorable or complete, optionally waits for BulkDump snapshot metadata, then discontinues the backup. `run_restore` starts `fdbrestore start` and polls status until completion or failure. `test_encryption_mismatches` asserts the expected failure matrix for encrypted and unencrypted backups. `run_restore_wait`, `setup_backup_test_environment`, and `setup_fdb_cluster_with_backup` support higher-level scripts.

## Control Flow

The helper expects strict-mode callers and uses bash namerefs to mutate argument arrays. Backup flow is deliberately non-blocking at first: it avoids `-w`, polls status for up to 10 minutes, logs progress every 30 seconds, and handles already-completed backups as success. For `bulkdump` or `both` snapshot modes, it runs an additional describe loop looking for `bulkDumpJobId` or `,bulk` because BulkDump snapshot metadata can appear after rangefile restorability. Restore flow similarly starts asynchronously and polls `fdbrestore status`, treating completed state, complete phase, or missing restore tag as success while rejecting aborted state or non-`None` `LastError`.

## State and Persistence Behavior

The helpers create and clean blobstore paths, scratch log directories, temporary encryption key files, and test clusters. They mutate the test database by loading, clearing, restoring, and validating data through external functions from `tests_common.sh`. They depend on global variables such as `USE_S3`, `KNOBS`, `TLS_CA_FILE`, `USE_PARTITIONED_LOG`, and `USE_ENCRYPTION_BLOCK_SIZE`.

## Dependencies and Integration Points

This script sources `../../fdbclient/tests/tests_common.sh` when available and is used by blob, directory, and BulkDump/BulkLoad tests. It integrates `fdbbackup`, `fdbrestore`, `s3client`, `backup_agent`, MockS3/AWS fixtures, TLS CA setup, and output matcher helpers.

## Risks and Edge Cases

The helpers parse human-readable CLI output, so output text changes can break tests. The BulkDump metadata wait only warns on timeout and proceeds, which helps avoid flakiness but can hide delayed BulkDump failures until restore or audit. Randomized encryption and partitioned-log toggles broaden coverage but make individual failures less reproducible unless logs preserve the chosen flags. The restore failure check avoids false positives from `LastError: None`, which is an important regression guard.

## Test Signals

This file is itself the test signal source for this subset. It checks restorable/completed backup status, BulkDump snapshot markers, restore phases, encryption mismatch failures, status JSON via `test_fdbcli_status_json_for_bkup`, data verification, and absence of Severity=40 logs.
