## sources/test-tools/syzkaller/pkg/kcov/kcov.go

Purpose: Go-native KCOV tracing for the current OS thread.

Important APIs/types/functions: `KCOVState`, `KCOVTraceResult`, `Trace`, `EnableTracingForCurrentGoroutine`, and `DisableTracing`.

Control flow: enabling locks the goroutine to its OS thread, opens `/sys/kernel/debug/kcov`, initializes trace size, mmaps the coverage buffer, and enables PC tracing. `Trace` resets the count, runs a callback, copies collected PCs, and returns callback error plus coverage. Disable issues ioctl disable, unmaps, closes file, and unlocks the thread.

State and persistence: per-thread file descriptor and mmap buffer. No persistent files, but uses kernel debugfs.

Dependencies and integration: used by `kfuzztest-executor` to collect coverage for local KFuzzTest calls; depends on Linux KCOV and `golang.org/x/sys/unix`.

Risks: must pair enable/disable or the goroutine remains locked and resources leak. `Trace` trusts kernel count when creating an unsafe slice. Requires root/debugfs permissions and KCOV-enabled kernel.

Test signals: no direct unit tests; exercised only in Linux integration scenarios.
