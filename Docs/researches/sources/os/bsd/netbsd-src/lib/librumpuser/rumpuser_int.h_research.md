# File Research: sources/os/bsd/netbsd-src/lib/librumpuser/rumpuser_int.h

## Summary
Internal helper header for rumpuser implementation files.

## Key Details
- Declares the shared `rumpuser__hyp` hypervisor upcall table.
- Defines inline `rumpkern_unsched` and `rumpkern_sched` wrappers around backend schedule hooks.
- Provides `KLOCK_WRAP`, `DOCALL`, and `DOCALL_KLOCK` macros for host calls that must be made outside rump kernel scheduling.
- Defines fatal-check macros `NOFAIL` and `NOFAIL_ERRNO`.
- Declares internal thread init, signal translation, errno translation, and random initialization helpers.
- Defines `ET` so NetBSD returns native errors directly while other hosts translate them to rump errno values.

## Notes
This header centralizes the schedule-boundary convention used across file, BIO, clock, and component code.
