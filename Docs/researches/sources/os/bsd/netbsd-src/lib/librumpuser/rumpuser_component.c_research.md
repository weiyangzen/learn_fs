# File Research: sources/os/bsd/netbsd-src/lib/librumpuser/rumpuser_component.c

## Summary
Exports stable component-facing wrappers around rumpuser scheduling, LWP, and errno translation operations.

## Key Details
- `rumpuser_component_unschedule` unschedules the rump kernel and returns the saved lock count as an opaque cookie.
- `rumpuser_component_schedule` restores scheduling from that cookie.
- Provides component helpers for creating/releasing kernel-thread LWP context, reading current LWP, and switching LWP.
- `rumpuser_component_errtrans` exposes host-to-rump errno translation.

## Notes
The file comments distinguish these component ABI functions from the broader rump kernel/hypervisor contract versioned by `RUMPUSER_VERSION`.
