# sources/storage-engines/foundationdb/fdbclient/tests/fdb_cluster_fixture.sh

## Purpose
This Bash fixture starts and stops local loopback FoundationDB clusters for integration tests. It also provides a helper to start `backup_agent` against the generated cluster file.

## Important APIs, Types, And Functions
The exported surface is the global `FDB_PIDS` array plus `shutdown_fdb_cluster`, `start_fdb_cluster`, and `start_backup_agent`. `start_fdb_cluster` invokes `tests/loopback_cluster/run_custom_cluster.sh` with selected role counts, storage count, storage engine, knobs, and PID dumping.

## Control Flow
Startup builds a knob string with `--knob_shard_encode_location_metadata=true` and optional extra knobs, then retries port prefixes starting at 1600 in increments of 100. It temporarily disables `errexit` and `noclobber` around cluster startup, extracts `PIDS=` from output with retries, checks `fdbcli status`, retries only on "Local address in use", and otherwise prints stderr and fails. Shutdown sends SIGTERM to tracked PIDs, waits briefly, sends SIGKILL to survivors, and reports any remaining processes within a 15-second budget.

## State And Persistence Behavior
The fixture creates a `loopback_cluster` under the supplied scratch directory, writes output and stderr capture files, and stores tracked process IDs in memory. It does not delete scratch directories directly; caller cleanup owns file removal.

## Dependencies And Integration Points
It depends on the FoundationDB source tree, built `fdbcli`, `backup_agent`, loopback cluster scripts, POSIX process tools, and shared `err`/`log` functions when sourced by tests.

## Risks And Edge Cases
PID extraction depends on textual `PIDS=` output and may produce malformed entries if output contains unexpected binary/text data. Shutdown is intentionally aggressive and can kill only tracked processes, leaving untracked children if PID extraction failed. Knobs are passed as a single string, so quoting-sensitive values require care.

## Test Signals
Startup success is `fdbcli status` against `${scratch}/loopback_cluster/fdb.cluster`. Cleanup signal is no remaining tracked process and logs showing SIGTERM/SIGKILL completion within the shutdown budget.
