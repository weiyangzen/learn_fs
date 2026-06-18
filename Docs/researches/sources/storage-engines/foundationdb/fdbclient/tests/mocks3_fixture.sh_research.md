# sources/storage-engines/foundationdb/fdbclient/tests/mocks3_fixture.sh

## Purpose
This fixture starts a local MockS3Server by running the built `fdbserver` with role `mocks3server`. It provides a fast local blobstore backend for CTests when real S3/GCS is unavailable or undesired.

## Important APIs, Types, And Functions
Important globals are `MOCKS3_HOST`, `MOCKS3_PORT`, `MOCKS3_PID`, and `MOCKS3_LOG_FILE`. Functions are `start_mocks3`, `shutdown_mocks3`, and `get_mocks3_url`, exported for scripts that source the fixture.

## Control Flow
`start_mocks3` accepts optional build and persistence directories, discovers a build directory if omitted, validates `bin/fdbserver`, and tries up to ten ports. Each attempt starts `fdbserver --role mocks3server --public-address host:port --listen-address host:port`, optionally with persistence and log directories, waits a few seconds, treats process death plus bind-related log patterns as a retryable port conflict, and otherwise returns ready. Shutdown sends SIGTERM, waits up to about a second, sends SIGKILL if needed, logs unkillable process info, and removes the temporary stderr log.

## State And Persistence Behavior
It stores object data in the optional persistence directory, writes trace logs near that directory, and keeps PID/log-path state in shell globals. Failed bind attempts remove temporary logs and matching trace files to avoid false `Severity=40` test failures.

## Dependencies And Integration Points
The fixture depends on a built FoundationDB binary that supports `--role mocks3server`, POSIX process control, `mktemp`, and optional persistence directories. It integrates with `tests_common.sh`, `s3client_test.sh`, and `bulkload_test.sh` through URL/host/port variables.

## Risks And Edge Cases
Readiness is time-based after several seconds rather than an HTTP health check, so a slow or partially initialized server may still be reported ready. `set -e` in a sourced fixture can affect parent script behavior. Global `MOCKS3_PORT` is mutated on conflict and reused by URL builders.

## Test Signals
Signals are "MockS3Server ready" logs, a live tracked PID, successful `blobstore://mocks3:mocksecret@host:port` operations, and clean shutdown without lingering processes or severity-40 traces from failed bind attempts.
