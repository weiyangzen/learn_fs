# sources/object-store/minio/cmd/os-instrumented.go

## Purpose
This file wraps common filesystem operations with MinIO OS metrics and optional trace publication. It is the instrumentation entry point for operations such as remove, mkdir, rename, open, stat, direct I/O open, and fdatasync.

## Important APIs, Types, and Functions
`osMetric` enumerates tracked operation classes and is paired with generated string output in `osmetric_string.go`. `globalOSMetrics` stores lifetime counters and last-minute latency buckets. `updateOSMetrics` returns a deferred closure that records duration and, when OS trace subscribers exist, publishes `madmin.TraceInfo` via `globalTrace`.

The exported wrappers are `RemoveAll`, `Mkdir`, `MkdirAll`, `Rename`, `OpenFile`, `Access`, `Open`, `OpenFileDirectIO`, `Lstat`, `Remove`, `Stat`, `Create`, and `Fdatasync`. `init` injects `OpenFile`, `OpenFileDirectIO`, and `Open` into `internal/ioutil` hooks so shared IO helpers automatically use instrumentation.

## Control Flow and State
Each wrapper defers a closure returned by `updateOSMetrics`, then calls the underlying standard-library, disk, or platform-specific helper. `OpenFile` chooses read or write metrics by masking flags with `writeMode`. The metrics state is process global and uses atomic counters plus `lockedLastMinuteLatency`.

## Dependencies and Integration Points
The file integrates with `madmin.OSMetrics`, `globalTrace`, `globalLocalNodeName`, `disk.OpenFileDirectIO`, `disk.Fdatasync`, and platform-specific helpers from `os_unix.go`, `os_windows.go`, or `os_other.go`.

## Risks and Test Signals
Tracing can include paths, so subscribers receive sensitive filesystem paths. Metrics depend on every caller using these wrappers rather than raw `os` functions. The direct test signal is limited in this subset, but OS read/rename/mkdir tests exercise wrappers indirectly through `Mkdir`, `Rename`, and `Open`.
