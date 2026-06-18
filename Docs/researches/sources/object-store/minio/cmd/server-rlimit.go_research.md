# sources/object-store/minio/cmd/server-rlimit.go

Purpose: This file centralizes process resource-limit tuning and a Linux kernel age check used during server startup. It tries to raise Go runtime and OS limits to values suitable for MinIO's high-concurrency object server workload.

Important APIs and types: `oldLinux` calls `kernel.CurrentVersion` and compares it to `kernel.Version(4,0,0)`. `setMaxResources` reads max kernel threads, open-file limits, virtual memory limits, and optional `serverCtxt.MemLimit`; it calls `debug.SetMaxThreads`, `sys.SetMaxOpenFileLimit`, and `debug.SetMemoryLimit`.

Control flow: `oldLinux` returns false if the kernel cannot be probed or returns zero, otherwise reports whether it is older than Linux 4.0. `setMaxResources` sets Go's max thread count to 90% of the kernel setting when above the default threshold, retrieves the max file descriptor limit, warns if it is below 4096 on non-Windows, sets the soft/hard open-file limits to the maximum, warns for very small virtual memory limits, applies a Go memory limit if configured, and deliberately avoids setting RLIMIT_AS.

State and persistence behavior: There is no application persistence. The function mutates process/runtime limits for the running server process and may change OS resource-limit soft values. It logs warnings for low production limits.

Dependencies and integration points: `serverMain` calls `setMaxResources` during bootstrap and uses `oldLinux` to append startup warnings. The file depends on MinIO's `serverCtxt`, `logger`, `sys` package abstractions, `madmin-go/kernel`, Go runtime/debug, and `humanize`.

Risks: Resource-limit changes are platform-sensitive and permission-sensitive. Errors from open-file or memory-limit probing propagate, but `serverMain` currently ignores the returned error. Raising max threads and file limits can fail under containers or restricted services. The code intentionally avoids RLIMIT_AS because small values can crash the Go runtime.

Test signals: There are no direct tests here. Indirect signals are startup warnings for old kernels or low limits, and successful server boot under constrained environments.
