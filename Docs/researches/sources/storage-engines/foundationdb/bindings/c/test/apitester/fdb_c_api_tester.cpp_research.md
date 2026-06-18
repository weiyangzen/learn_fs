# sources/storage-engines/foundationdb/bindings/c/test/apitester/fdb_c_api_tester.cpp

## Purpose
Main executable for FoundationDB C API TOML workloads. It parses CLI/TOML config, applies FDB network options, starts the network thread, creates scheduler/executor/workloads, and returns based on workload success.

## Important APIs, types, and functions
`parseArgs`, `processArg`, `applyNetworkOptions`, `randomizeOptions`, and `runWorkloads` handle command-line options, external clients, TLS, tracing, knobs, random concurrency, transaction executor options, scheduler creation, and workload manager setup.

## Control flow
`main` parses and randomizes options, selects capped API version, applies network options before setup, runs FDB network on a thread, runs workloads, performs ASAN cleanup flushing when enabled, stops the network, and joins.

## State and persistence behavior
Writes trace logs when enabled, creates temp files through the executor, and persists workload data in the target cluster. FDB network options are process-global and immutable after setup.

## Dependencies and integration points
Integrates `TesterOptions`, `TesterTestSpec`, scheduler, transaction executor, workload framework, `test/fdb_api.hpp`, TLS/external client options, and the Python runners.

## Risks and test signals
Option ordering is critical. Randomized settings improve coverage but complicate reproduction. Signals are process exit code, workload stderr summaries, trace files, and stats output.
