# sources/storage-engines/foundationdb/fdbbackup/tests/blob_backup_restore_test.sh

## Purpose

`blob_backup_restore_test.sh` is an end-to-end backup and restore test for blob storage using S3, GCS, Azure, or MockS3Server depending on environment. It validates that data can be backed up to blob storage, cleared from FoundationDB, restored, and verified, with optional encryption and partitioned mutation-log coverage.

## Important APIs, Types, and Functions

The script defines `cleanup`, `resolve_to_absolute_path`, and `test_s3_backup_and_restore`. The test function pre-clears the target object path, loads data, calls shared `run_backup`, checks backup status JSON, clears data, runs encryption mismatch tests, calls shared `run_restore`, verifies data, cleans the blob path, and scans logs for Severity=40.

## Control Flow

Strict bash options are enabled after function definitions. The script randomly chooses `USE_ENCRYPTION` and `USE_PARTITIONED_LOG`; if encryption is enabled, it may also randomly set `USE_ENCRYPTION_BLOCK_SIZE`. It resolves its directory, sources `tests_common.sh` and `backup_tests_common.sh`, sets up provider-specific blobstore environment with `setup_backup_test_environment` and `setup_s3_environment`, starts a one-process FDB cluster plus backup agent, constructs a `blobstore://` URL, and runs the test.

Cleanup is installed for process termination and normal exit. It uses a 30-second watchdog, respects preservation mode, shuts down FDB and blob fixtures, calls AWS cleanup if available, and removes the encryption key file.

## State and Persistence Behavior

The script mutates a temporary FDB cluster, blobstore bucket/prefix, scratch logs, and optionally an encryption key file. For real S3, KMS encryption knobs and TLS CA handling are inherited from common setup. The target cleanup URL rewrites `ctest` to `data/ctest`, matching backup container layout behavior.

## Dependencies and Integration Points

It depends on `backup_tests_common.sh`, shared FDB test fixtures, MockS3/AWS setup, `fdbbackup`, `fdbrestore`, `backup_agent`, and status/data verification helpers. It directly exercises `backup.cpp` options for blob credentials, encryption key file, encryption block size, partitioned mutation logs, cluster file, tag, destination container, and restore container.

## Risks and Edge Cases

Randomized feature selection can expose interactions but makes failure reproduction depend on logged globals. Cleanup must tolerate missing functions because failures can happen before all fixtures are sourced or started. The test assumes the edited cleanup URL accurately tracks the container data path. The encryption mismatch checks intentionally run before successful restore, so they must not leave persistent restore state that interferes with the real restore tag.

## Test Signals

Passing this script signals that blob credentials, object cleanup, backup agent status, blob backup submission, restorable polling, restore polling, encryption mismatch handling, data verification, and fatal-log scanning all work for the selected provider mode.
