# File Research: sources/os/bsd/freebsd-src/sys/sys/callout.h

## Purpose
`callout.h` defines FreeBSD kernel timer/callout flags and scheduling APIs.

## Main Interfaces
- Internal/external callout flags track active, pending, processed, shared-lock, deferred migration, direct execution, and handler lock-return behavior.
- Scheduling flags support direct execution, precision encoding, hardclock alignment, absolute times, precalculated times, and signal-catching sleeps.
- Macros expose `callout_active`, `callout_deactivate`, `callout_pending`, `callout_drain`, reset/schedule variants, and CPU-local scheduling.
- Functions initialize callouts, reset them with sbintime precision, schedule/stop/drain, process callouts, and compute effective time/precision.

## Implementation Notes
The header distinguishes caller-visible `c_flags` from subsystem-owned `c_iflags`. The comments stress that callers must hold their own lock when manipulating visible state to avoid races.

## Dependencies and Constraints
Kernel-only APIs depend on `sys/_callout.h`, lock objects, `PCPU_GET(cpuid)`, and `tick_sbt`. `CALLOUT_MPSAFE` remains as deprecated compatibility.
