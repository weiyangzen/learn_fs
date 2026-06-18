# sources/storage-engines/foundationdb/contrib/local_cluster/local_cluster.py

## Purpose
The top-level `local_cluster.py` script starts a local FoundationDB cluster and keeps it running until interrupted.

## Important APIs, Types, And Functions
`_setup_logs` configures stderr logging. `_setup_args` parses `--num-processes`, `--work-dir`, `--debug`, `--cluster-file`, `--fdbserver-path`, `--fdbcli-path`, and `--port`. `run_fdbservers` opens an async `FDBServerLocalCluster` context and sleeps forever. `main` validates process count, sets executable paths, and runs the async loop.

## Control Flow
CLI execution parses args and logging, rejects fewer than one process, configures binary paths through `lib.fdb_process`, then runs `run_fdbservers`. The async function starts the cluster and then loops with one-second sleeps, relying on context-manager exit during cancellation or exceptions for cleanup.

## State And Persistence Behavior
Runtime state and persistence are delegated to `lib.local_cluster.FDBServerLocalCluster`: work directories, cluster file, fdbserver data, and logs. The script itself persists nothing else.

## Dependencies And Integration Points
It depends on sibling `lib.local_cluster` and `lib.fdb_process`, `asyncio`, and external FoundationDB binaries. It is the operator-facing entry point for manually starting a local cluster from this contrib package.

## Risks And Edge Cases
The infinite loop has no explicit signal handling in this file. Work directories remain by default. It uses `asyncio.get_event_loop().run_until_complete`, which is older style compared with `asyncio.run`. The error message says "more than 1 process" even though one process is accepted.

## Test Signals
Tests should mock `FDBServerLocalCluster` and path setters, assert argument parsing and process-count validation, and verify the async context is entered. Integration tests can run with real binaries and confirm the cluster remains available until terminated.
