# sources/storage-engines/foundationdb/fdbserver/fdbserver.cpp

## Purpose
Main `fdbserver` executable entrypoint. It owns process-wide initialization, command-line parsing, network/simulator selection, trace/log setup, knob initialization, role dispatch, and final exit handling for server, simulation, tests, maintenance, and utility roles.

## Important APIs, Types, and Functions
- `g_rgOptions` defines SimpleOpt command-line options for addresses, cluster files, roles, memory, TLS, tracing, tests, filesystem validation, blob credentials, MockS3, authorization keys, and protocol toggles.
- `ServerRole` enumerates dispatch targets including `FDBD`, `Simulation`, `Test`, `MultiTester`, `UnitTests`, network tests, KV file utilities, consistency checks, cluster-key change, and `MockS3Server`.
- `CLIOptions` stores parsed runtime configuration: paths, role, addresses, TLS, knobs, localities, memory budgets, credentials, profiler config, allowlist, and role-specific values.
- `CLIOptions::parseArgs`, `parseArgsInternal`, and `parseEnvInternal` validate arguments, read environment knobs/proxy/blob credentials, seed deterministic randomness, and load or synthesize cluster connection files.
- `buildNetworkAddresses` and `CLIOptions::buildNetwork` validate public/listen addresses, auto-addresses, TLS state, secondary address rules, and consistency-check synthetic addresses.
- `getSharedMemoryMachineId`, `validateSimulationDataFiles`, and `main` handle shared machine identity, simulation folder safety, and top-level runtime dispatch.

## Control Flow
Startup performs platform/crash/profiling setup, parses options, initializes buggify/fault injection, resets server knobs, applies explicit knobs, creates the simulator or Net2/FlowTransport stack, opens tracing, initializes TLS/filesystem/metrics, emits `ProgramStart`, starts memory monitoring, and dispatches by `ServerRole`.

Simulation validates and prepares the simulation data folder, handles restart/restore metadata from `restartInfo.ini`, restores snapshotted role files, applies persisted knobs, and runs `simulationSetupAndRun`. The `FDBD` role starts `fdbd(...)` plus histogram and metrics actors. Test roles call `runTests`, network roles call `networkTestClient/server`, KV roles call KV file utilities, cluster-key change calls `coordChangeClusterKey`, and MockS3 starts the real mock S3 server.

## State and Persistence Behavior
Persistent effects include cluster connection files, data/tlog-spill directories, trace logs, metrics output, simulation restart metadata, restore snapshots, MockS3 persistence, blob credential files, authorization public keys, and optional shared-memory machine IDs. Fresh simulation runs can recursively erase the simulation data folder after validation.

## Dependencies and Integration Points
This file integrates Flow/Net2, FlowTransport, TLS, simulator, worker roles, data distributor tests, KV file utilities, MockS3, coordination utilities, backup credential plumbing, metrics, tracing, actor lineage profiling, fault injection, buggify, Swift concurrency hooks, and platform filesystem helpers.

## Risks and Edge Cases
Address/TLS validation is security-sensitive. Simulation cleanup is destructive when not restarting. Seed cluster-file handling must reject conflicts and malformed descriptions. Memory/cache limits can abort startup. Role dispatch depends on earlier validation. Shared-memory machine identity has platform permission subtleties. Build flags and platform macros materially change behavior.

## Test Signals
The file directly drives simulation, unit tests, network tests, KV file checks, and consistency checks. Simulation treats logged `SevError` events as failure signals and prints random unseed/elapsed time for reproducibility.
