# File Research: sources/os/bsd/freebsd-src/sys/kern/ksched.c

## Purpose
Provides the kernel scheduler adapter for POSIX P1003.1B realtime scheduling APIs. It maps POSIX policies and priorities onto FreeBSD's `rtprio`/scheduler priority model.

## Key Elements
- Defines `FEATURE(kposix_priority_scheduling, ...)`.
- `struct ksched` stores the round-robin interval reported through POSIX APIs.
- `ksched_attach()` allocates scheduler state and computes `rr_interval` from `hz` and `sched_rr_interval()`.
- `ksched_detach()` frees scheduler state.
- `getscheduler()` maps `RTP_PRIO_FIFO` to `SCHED_FIFO`, `RTP_PRIO_REALTIME` to `SCHED_RR`, and other classes to `SCHED_OTHER`.
- `ksched_setparam()`, `ksched_getparam()`, `ksched_setscheduler()`, and `ksched_getscheduler()` implement POSIX parameter/policy operations.
- `ksched_yield()` delegates to `sched_relinquish(curthread)`.
- `ksched_get_priority_max()`, `ksched_get_priority_min()`, and `ksched_rr_get_interval()` expose POSIX limits.

## Priority Model
POSIX treats numerically higher values as higher priority, while traditional FreeBSD priorities use lower numeric values for higher priority. The file centralizes conversions with:
- `p4prio_to_rtpprio()` / `rtpprio_to_p4prio()` for realtime priorities.
- `p4prio_to_tsprio()` / `tsprio_to_p4prio()` for timeshare priorities.

## Integration
The code depends on scheduler primitives in `<sys/sched.h>` and priority conversion helpers `pri_to_rtp()` and `rtp_to_pri()`. It is called by `p1003_1b.c` after syscall-layer permission checks have selected and locked the target thread/process.

## Notable Edge Cases
- `SCHED_OTHER` priority handling is implementation-defined and maps into the timeshare range.
- Invalid priorities or policies return `EINVAL`.
- `ksched_getparam()` clamps or interprets timeshare priority state so POSIX callers see the expected ascending priority scale.
