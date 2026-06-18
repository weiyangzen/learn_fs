# File Research: sources/os/bsd/netbsd-src/lib/librumpuser/rumpuser.c

## Summary
Core POSIX rumpuser hypercall support for the normal threaded backend.

## Key Details
- Validates `RUMPUSER_VERSION`, initializes randomness and threading, and stores the hypervisor upcall table in `rumpuser__hyp`.
- Implements rump clock queries and sleeps with `clock_gettime`, `nanosleep`, and optionally `clock_nanosleep`.
- Unschedules the rump kernel around blocking sleep operations, then reschedules with the saved lock count.
- Supplies parameters such as `RUMP_NCPU`, hostname, and arbitrary environment variables via `getenv_r`.
- Defaults `RUMP_NCPU` to `2`, with `RUMP_NCPU=host` mapped to `_SC_NPROCESSORS_ONLN`.
- Provides putchar, process exit/panic behavior, errno setting, debug printing, host signal raising, and page-size query.

## Notes
The absolute monotonic sleep path falls back to realtime polling plus relative sleeps when `clock_nanosleep` is unavailable.
