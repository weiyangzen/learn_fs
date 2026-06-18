# sources/sync-backup/syncthing/test/usage_windows.go

Purpose: Windows implementation of benchmark process CPU reporting for Syncthing transfer benchmarks, compiled under `integration && benchmark && windows`.

Important APIs/functions: `ftToDuration` converts a Windows `syscall.Filetime` to `time.Duration`, although current code uses the `Nanoseconds()` methods on `Rusage.UserTime` and `KernelTime`. `printUsage` logs user and kernel time per MiB.

Control flow: `printUsage` type-asserts `proc.SysUsage()` to `*syscall.Rusage`, computes MiB from total transferred bytes, and logs user/kernel time normalized by transfer size.

State/persistence: no filesystem or process state mutation; it reads the already-finished child process state.

Dependencies/integration: called by `benchmarkTransfer` in the benchmark file after stopping sender and receiver. It depends on Windows Go runtime support for `ProcessState.SysUsage`.

Risks: `ftToDuration` is dead code and may indicate an older conversion path. As with Unix, `mib` must be nonzero. No RSS/memory metric is logged on Windows, so cross-platform benchmark comparisons are CPU-only there.

Test signals: benchmark logs should show `Utime` and `Stime` per MiB for each Syncthing process on Windows.
