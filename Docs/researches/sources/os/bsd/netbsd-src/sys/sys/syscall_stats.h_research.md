# File Research: sources/os/bsd/netbsd-src/sys/sys/syscall_stats.h

This header defines optional syscall counting and timing instrumentation for the kernel.

Key interface details:
- Includes `opt_syscall_stats.h` under `_KERNEL_OPT`.
- Under `SYSCALL_STATS`, declares:
  - `syscall_counts[SYS_NSYSENT]`,
  - aggregate user/system/interrupt counters,
  - `SYSCALL_COUNT(table, code)`.
- Under `SYSCALL_TIMES` and `__HAVE_CPU_COUNTER`, uses `<machine/cpu_counter.h>` to measure syscall elapsed cycles.
- Provides macros for LWP init, syscall entry, sleep, wakeup, syscall exit, and disabled interrupt hooks.
- Can optionally update per-process tick fields when `SYSCALL_TIMES_PROCTIMES` is enabled.
- Falls back to no-op macros when stats/timing support is not configured.

Research notes:
- This file is compile-time instrumentation glue; it has no runtime storage unless the relevant options are enabled.
- Timing uses a 32-bit CPU counter, so consumers must treat deltas as wrap-safe unsigned arithmetic.
- The default no-op definitions let syscall paths call these macros without feature-specific conditionals.
