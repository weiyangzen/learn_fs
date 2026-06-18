# sources/storage-engines/foundationdb/fdbclient/tests/bulkload_test.sh

## Purpose
This integration test validates FoundationDB bulkdump and bulkload using either real S3/GCS or MockS3Server. It starts a loopback cluster, writes data, dumps the full key range to blobstore, clears the database, restores from the dump, verifies data, and checks logs for severity 40 errors.

## Important APIs, Types, And Functions
Main functions are `cleanup`, `resolve_to_absolute_path`, `bulkdump`, `bulkload`, and `test_basic_bulkdump_and_bulkload`. The script uses shared helpers from `tests_common.sh` (`load_data`, `clear_data`, `verify_data`, `grep_for_severity40`, `setup_s3_environment`), `fdb_cluster_fixture.sh` (`start_fdb_cluster`, `shutdown_fdb_cluster`), and cloud/mock fixtures.

## Control Flow
The script installs exit/signal traps, resolves its own directory, sources common helpers, derives `USE_S3`, sets TLS and encryption knobs, validates command-line source/build/scratch arguments, sets up the blobstore environment, sources the FDB cluster fixture, starts a loopback cluster with nine storage servers, and runs `test_basic_bulkdump_and_bulkload`. The test loads generated key/value data, optionally removes the target S3 prefix, enables bulkdump mode, starts a dump, polls until no dump is running, clears data, enables bulkload mode, adds the lock owner, starts load by job id, polls until completion, verifies values, and scans logs.

## State And Persistence Behavior
It creates scratch directories containing cluster files, logs, MockS3 persistence, credentials, and temporary outputs. Database state is deliberately mutated through load, clear, and restore phases. Cleanup normally tears down FDB, MockS3, AWS scratch state, and can preserve artifacts when `PRESERVE_TEST_DATA=1`.

## Dependencies And Integration Points
The test depends on built `fdbcli`, `s3client`, the loopback cluster script, blobstore fixture selection, and bulkdump/bulkload CLI commands. It passes blobstore URLs of the form `blobstore://host/path?bucket=...&region=...&secure_connection=...`.

## Risks And Edge Cases
`bulkdump` declares `local_url` but invokes `bulkdump dump ... "${url}"`, which relies on a global `url` rather than the parameter and is fragile. Poll loops have no explicit timeout, so stuck jobs can hang until the outer test timeout. Real S3 mode uses KMS encryption knobs and may fail on IAM/KMS policy drift. The script uses `set -euo pipefail` plus sourced fixtures that can `exit`.

## Test Signals
Strong signals are a captured dump job id, successful `bulkload status` convergence to no running job, exact restored values from `verify_data`, and absence of `Severity="40"` traces outside excluded directories.
