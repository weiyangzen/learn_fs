# sources/storage-engines/pebble/bench/fsbench.go

## Purpose
`fsbench.go` implements filesystem microbenchmarks for create, delete, write+sync, and disk-usage operations through Pebble's `vfs.FS` interface. It is independent of Pebble DB state and measures filesystem behavior relevant to storage-engine performance.

## Important APIs, Types, And Functions
`FsBenchConfig`, `DefaultFsBenchConfig`, `FsBenchmark`, `FsBenchmarks`, and `RunFsBench` are exported. Internal `fsEnv` owns the filesystem, write buffer, and helpers; `fsBench` owns per-run state. Benchmark constructors include `createBench`, `deleteBench`, `deleteUniformBench`, `writeSyncBench`, and `diskUsageBench`. Execution methods are `init`, `execute`, `tick`, and `done`.

## Control Flow
`FsBenchmarks` builds a named registry. `RunFsBench` selects a benchmark, repeats it `NumTimes`, constructs the run state, and delegates to `RunTestWithoutDB`. Each benchmark closure prepopulates directories/files as needed, defines a `run` function that records one latency sample per operation, and defines cleanup/stop closures. `execute` loops until `run` returns false or `MaxOps` is reached.

## State And Persistence Behavior
This file deliberately creates, writes, syncs, deletes, and recursively removes files/directories. Some benchmarks prepopulate up to hundreds of thousands of files and multi-GiB file sizes. Cleanup tries to remove benchmark directories and close open handles, but interrupted or fatal exits may leave large artifacts.

## Dependencies And Integration Points
It depends on `vfs.FS`, `histogramRegistry`, `RunTestWithoutDB`, OS path/removal functions, atomics, and standard logging. CLI code selects names returned by `FsBenchmarks`.

## Risks And Edge Cases
Risks include very large disk usage, `log.Fatal` aborts before cleanup, shared `numFiles`/file handle state only safe because each `fsBench` currently runs a single worker, and use of `os.RemoveAll` in `fsEnv.removeAll` rather than the configured `vfs.FS`. Directory handles are synced for create/delete timing but platform behavior may differ.

## Test Signals
No direct tests. Outputs are benchmark histograms and `Benchmarkfsbench/...` lines. Manual validation should use small `MaxOps` and scratch directories.
