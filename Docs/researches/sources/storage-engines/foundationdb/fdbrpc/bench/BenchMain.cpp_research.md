# sources/storage-engines/foundationdb/fdbrpc/bench/BenchMain.cpp

## Purpose
`BenchMain.cpp` is the entry point for fdbrpc benchmarks. It initializes the Net2 filesystem and delegates command-line handling to the shared Flow benchmark runner.

## Important APIs, Types, and Functions
The file defines `initializeNet2FileSystem` and `main`. Initialization registers `Net2FileSystem::stop` as a network stop callback and installs a new Net2 filesystem.

## Control Flow
`main` calls `runBenchmarks(argc, argv, initializeNet2FileSystem)`. The benchmark runner owns benchmark registration, argument parsing, network setup, and execution; this file provides fdbrpc-specific filesystem setup.

## State and Persistence Behavior
It mutates process-global `g_network` callbacks and the global `IAsyncFileSystem` implementation. It does not persist data directly.

## Dependencies and Integration Points
It depends on `fdbrpc/Net2FileSystem.h` and `flow/BenchMain.h`. It is linked into the `fdbrpc_bench` executable built by the bench CMake file.

## Risks and Edge Cases
Benchmarks that assume a different filesystem implementation will inherit Net2. Stop-callback ordering matters if other benchmark initialization also registers filesystem or network cleanup.

## Test Signals
Successful startup and benchmark discovery indicate that Net2 filesystem initialization and benchmark registration are wired correctly.
