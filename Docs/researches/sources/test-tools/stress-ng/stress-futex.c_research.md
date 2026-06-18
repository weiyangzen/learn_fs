<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-futex.c -->
# sources/test-tools/stress-ng/stress-futex.c Research

Purpose: implements `futex`, a Linux scheduler/OS/IPC stressor that repeatedly exercises futex wait and wake paths between a parent waker and child waiter.

Important APIs/types/functions: `stress_futex_wait()` wraps `shim_futex_wait()` and periodically tries `shim_futex_waitv()` when `FUTEX_32` and `CLOCK_MONOTONIC` are available, disabling waitv after errors or ENOSYS. `stress_futex()` forks the waiter, drives wake calls, and records timeout counts in `g_shared->futex.timeout[instance]`. `stress_futex_info` registers the stressor or an unimplemented placeholder without Linux futex support.

Control flow: after synchronization, the parent records its CPU and forks. Fork failures may retry through `stress_redo_fork()`. The parent loops calling `shim_futex_wake(futex, 1)` until stop, optionally verifying wake errors, then SIGALRMs and waits for the child. The child pins toward the parent CPU, applies scheduler settings, sets parent-death alarm behavior, and loops on short 5000 ns futex waits. Timeouts increment a shared counter and trigger periodic backoff sleeps after thresholds; non-timeout wakeups increment bogo operations. The child exits with failure if verify mode sees unexpected wait errors.

State and persistence: futex words and timeout counters live in stress-ng shared memory. The child process is transient and reaped. No durable state exists.

Dependencies and integration: depends on Linux futex headers and `__NR_futex`, stress-ng futex shims, CPU affinity helpers, shared state, fork retry logic, scheduler settings, and signal/wait helpers. Verification is optional.

Risks: futex waitv availability depends on kernel support and is dynamically disabled. Very fast timeout polling can consume CPU and trigger scheduler artifacts; the threshold backoff mitigates this. Parent/child status handling does not propagate child failure status beyond wait completion in the parent path.

Test signals: watch bogo progress, debug timeout counts, and optional verification errors for futex wait/wake. Test on kernels with and without `futex_waitv`, under CPU affinity constraints, and under fork pressure.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-futex.c -->
