# sources/test-tools/fio/t/client_server.py

## Purpose
Regression harness for fio client/server mode. It starts four local fio daemon servers, runs command-line client jobs against one or more servers, and validates JSON output for global option propagation and aggregated latency percentile reporting.

## Important APIs, Types, and Functions
`ClientServerTest` extends `FioJobCmdTest` and builds `--client=<server> <jobfile>` argument pairs. `ClientServerTestGlobalSingle` validates a single job file's `[global]` section against JSON `global options`. `ClientServerTestGlobalMultiple` validates the array form used with multiple clients. `ClientServerTestAllClientsLat` checks the `All clients` aggregate for expected `slat`, `clat`, and `lat` percentile presence. `start_servers()`, `stop_servers()`, `parse_args()`, and `main()` drive server lifecycle and runner setup.

## Control Flow
`main()` creates an artifact directory, resolves the fio binary, daemonizes servers on ports 8765-8768, rewrites test specs from server/job indexes into concrete paths, then delegates to `run_fio_tests()`. Each test creates one fio client invocation and inherits JSON decoding and basic success checks from `FioJobCmdTest`. After tests, the script kills the daemon PIDs from pidfiles and exits with the failure count.

## State and Persistence Behavior
State is stored in artifact subdirectories through the common runner: command, stdout, stderr, exit code, and JSON output files. Runtime server PID files are created with `tempfile.mktemp()` and tracked in `PIDFILE_LIST`. The script mutates `TEST_LIST` in place by replacing server indexes and relative jobfile names with concrete values.

## Dependencies and Integration Points
Depends on a built fio executable, local TCP/loopback ports, job files under `t/client_server`, Python `configparser`, and `fiotestlib` runner semantics. It directly validates fio's client/server JSON schema, especially `global options` and `client_stats`.

## Risks
Fixed ports can collide with existing services. `tempfile.mktemp()` is race-prone. A server startup failure exits before cleanup of already-started servers. `stop_servers()` uses `kill` directly and is Unix-oriented. In-place `TEST_LIST` mutation means repeated `main()` calls in the same interpreter would corrupt server indexes.

## Test Signals
Passing tests indicate basic client/server operation, single and multi-client global option reporting, no-global behavior, mixed global array matching by host/port, and correct all-client latency percentile inclusion or exclusion for `slat`, `clat`, and `lat`.
