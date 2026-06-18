# Research: sources/object-store/minio-mc/cmd/profiling.go

## sources/object-store/minio-mc/cmd/profiling.go

Purpose: implements optional runtime profiling controlled by `MC_PROFILER` in `main.go`.

Important APIs and types: `profiler` interface; concrete `cpuProfiler`, `memProfiler`, `blockProfiler`, and `goroutineProfiler`; constructors for each; package-global `globalProfilers`; `enableProfilers` and `stopProfiling`.

Control flow: `enableProfilers` creates the output folder, opens one timestamped file per requested profiler, constructs the matching profiler, starts it, and stores it globally. CPU starts immediately; memory and goroutine write snapshots on stop; block enables `runtime.SetBlockProfileRate(100)` until stop. `stopProfiling` stops all registered profilers in order.

State and persistence: writes profile files under the profile directory. Mutates global profiler list and runtime block profiling rate.

Dependencies and integration: called from `Main` when `MC_PROFILER` is set and from ping signal handling before global cancellation.

Risks and tests: if an unknown profiler appears after earlier profilers started, the function returns an error without stopping already-started profilers or closing files. No direct tests.

<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/profiling.go -->
