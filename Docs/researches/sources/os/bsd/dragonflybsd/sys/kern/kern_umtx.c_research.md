# File Research: sources/os/bsd/dragonflybsd/sys/kern/kern_umtx.c

Implements userland mutex sleep/wakeup helper syscalls operating on user addresses translated to physical wait addresses.

Key sysctls:
- `kern.umtx_delay` when RDTSC is supported: nanoseconds to spin before sleeping.
- `kern.umtx_timeout_max`: maximum sleep timeout in microseconds, default 2,000,000.

Key APIs:
- `sys_umtx_sleep()`
- `sys_umtx_wakeup()`

Important behavior:
- `sys_umtx_sleep()` validates timeout and alignment, reads the user int, translates the user virtual address to a physical address via `uservtophys()`, and sleeps only if the current value matches the expected value.
- It tolerates temporary translation discontinuities with retry loops and emits diagnostics if retries are exhausted.
- With RDTSC support, it spin-polls briefly before sleeping to avoid sleep/wakeup/IPI overhead on short-lived mutex contention.
- Sleep timeout is capped by `kern.umtx_timeout_max`, converted to ticks, and uses `tsleep_interlock()` plus `tsleep()` in `PDOMAIN_UMTX`.
- Before sleeping, it rechecks that the physical address did not change and rereads the user value to close wakeup races.
- `ERESTART` is converted to `EINTR`.
- `sys_umtx_wakeup()` translates the user pointer similarly and wakes either one waiter or all waiters in `PDOMAIN_UMTX`.

Concurrency model:
- Wait channel is physical address, not user virtual address, to interlock shared mappings.
- Mapping changes are not fully tracked; capped timeout and caller retry are part of the design.
- Critical sections tighten the sleep/wakeup interlock.

Filesystem relevance:
- No direct filesystem logic. It matters indirectly for threaded user programs doing filesystem I/O and for userland libraries using umtx primitives around file/path operations.
