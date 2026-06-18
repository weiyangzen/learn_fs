# sources/storage-engines/foundationdb/fdbbackup/tests/dir_backup_test.sh

## Purpose

`dir_backup_test.sh` is the local filesystem counterpart to the blob backup test. It verifies `file://` backup containers, restore from the most recent generated backup directory, optional file-level encryption, optional encryption block-size override, and optional partitioned mutation-log backup.

## Important APIs, Types, and Functions

The script defines `cleanup`, `resolve_to_absolute_path`, `backup`, `restore`, and `test_dir_backup_and_restore`. `backup` runs `fdbbackup start -w` against `file://${scratch_dir}/backups` with optional encryption and partitioned-log flags. `restore` finds the newest `backup-*` subdirectory and runs `fdbrestore start -w` against it. The top-level test loads data, backs up, checks status JSON, clears data, tests encryption mismatch behavior against the concrete backup path, restores, verifies data, and checks logs.

## Control Flow

The script uses strict bash mode, randomizes partitioned log and encryption options, resolves its directory, sources cluster and common test fixtures, sets `FDB_DATA_KEYCOUNT=10` for a smaller dataset, creates a temporary scratch directory, optionally creates an encryption key, starts a one-process cluster and backup agent, then runs the test.

Cleanup is trap-driven, guarded by a 30-second watchdog, respects preservation mode, shuts down the cluster, removes the scratch directory, and deletes the encryption key file.

## State and Persistence Behavior

Persistent test artifacts live under the temporary scratch directory: cluster files, logs, backup container directories, generated backup names, and encryption keys. The test database is loaded, cleared, restored, and verified. Unlike the shared asynchronous helper, `backup` and `restore` use `-w`, so command completion is the primary synchronization point.

## Dependencies and Integration Points

The script uses `fdb_cluster_fixture.sh`, `tests_common.sh`, `backup_tests_common.sh`, `fdbbackup`, `fdbrestore`, and `backup_agent`. It exercises local URL handling in `backup.cpp`, including the backup container path, tag handling, trace logs, encryption flags, and mutation log type.

## Risks and Edge Cases

The restore path is selected with `ls -dt ... | head -1`, which assumes backup directory naming and mtimes are reliable. There is a likely typo, `readonly sourcedir`, after assigning `source_dir`; if bash treats the missing variable as creating an empty readonly `sourcedir`, the actual `source_dir` remains usable but this line is suspicious. Randomized encryption settings again require logs for reproduction. Since `-w` is used, hung backup/restore behavior would rely on external CTest timeouts rather than the polling logic in the shared helper.

## Test Signals

Passing this script signals that local directory backup/restore works, status JSON is valid, encryption mismatch failures are enforced for local containers, restored data matches expected values, and no Severity=40 log events were produced.
