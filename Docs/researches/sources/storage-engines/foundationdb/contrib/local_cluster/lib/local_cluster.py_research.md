# sources/storage-engines/foundationdb/contrib/local_cluster/lib/local_cluster.py

## Purpose
`local_cluster.py` orchestrates a temporary local FoundationDB cluster from generated work directories, spawned `fdbserver` processes, and `fdbcli` configuration.

## Important APIs, Types, And Functions
`FDB_DEFAULT_PORT` is 4000. `configure_fdbserver(cluster_file)` waits for server response, runs `configure new single memory`, and waits for database availability. `spawn_fdbservers(num_processes, directory, cluster_file, port=None)` creates per-process data/log directories and starts `FDBServerProcess` instances. `FDBServerLocalCluster` is an async context manager exposing `work_directory`, `cluster_file`, `processes`, `handlers`, `run`, and `terminate`.

## Control Flow
`FDBServerLocalCluster.run` creates and sets up a `WorkDirectory`, generates a cluster file if needed, spawns the requested number of fdbservers on sequential ports, configures the database, logs readiness, and returns process handles. `__aenter__` calls `run`; `__aexit__` calls `terminate`. `terminate` sends SIGTERM and then SIGKILL to every process without waiting between them.

## State And Persistence Behavior
The cluster persists data and logs under the work directory during its lifetime. If no work directory is supplied, `WorkDirectory` creates a temp directory and, with default `auto_cleanup=False`, does not remove it on exit. The class stores process handles and handler objects in memory.

## Dependencies And Integration Points
It depends on sibling `cluster_file`, `fdb_process`, and `work_directory`. Top-level `local_cluster.py` and `binding_test.py` use `FDBServerLocalCluster` to provide a database.

## Risks And Edge Cases
Multi-process clusters still run `configure new single memory`, which may not match requested fault tolerance. `terminate` immediately sends kill after terminate and does not await process exit or reap handles. Work directories are not auto-cleaned by default. Existing cluster files must match the chosen port/process setup. Exceptions during spawn/configure can leave started processes running unless the caller handles cleanup.

## Test Signals
Tests should mock work directory setup, cluster file generation, process spawning, configure commands, wait helpers, context-manager cleanup, port increments, and failure paths during partial startup. Integration tests can verify a real local cluster reaches available status.
