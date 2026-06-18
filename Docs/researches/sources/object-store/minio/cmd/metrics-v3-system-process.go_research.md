# sources/object-store/minio/cmd/metrics-v3-system-process.go

This file defines the v3 `/system/process` metric loader for the current MinIO process. It declares metric names and `MetricDescriptor` values for goroutine count, uptime, CPU time, resident and virtual memory, file descriptor limits and open descriptors, process IO byte/syscall counters, and distributed namespace lock read/write totals.

The main APIs are `loadProcessMetrics`, `loadProcFSMetrics`, `loadProcStatMetrics`, and `loadProcIOMetrics`. `loadProcessMetrics` is a `MetricsLoaderFn`; it always records `runtime.NumGoroutine`, records uptime when `globalBootTime` is set, skips procfs collection on Windows and macOS, and otherwise uses `procfs.Self()` to load `/proc` stat, IO, limits, and fd counts. In distributed erasure mode it also reads `globalLockServer.stats()` to expose lock pressure.

Control flow is defensive and best-effort. Procfs failures are logged through `metricsLogIf` but do not fail collection; missing or zero values are simply omitted because `MetricValues.Set` only stores positive values. State is read-only against process globals and Linux procfs, with no persistence. Integration points are `metrics-v3.go` registration, the shared `MetricValues` descriptor validation layer, `globalLockServer`, `globalBootTime`, and platform constants.

Risks: zero-valued metrics disappear rather than reporting zero, which can confuse dashboards after restart or on idle nodes. Procfs support is Linux-centric. Lock metrics depend on a non-nil lock server and distributed mode. Test signal is indirect: no dedicated test exists, so coverage comes through v3 metrics integration and the descriptor contract.
