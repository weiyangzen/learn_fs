# File Research: sources/os/bsd/dragonflybsd/sys/sys/lwp.h

Defines user ABI for lightweight process creation and control. `lwp_params` supplies entry function, argument, stack, and two tid copyout addresses. User-visible APIs include `lwp_create`, `lwp_create2`, `lwp_gettid`, name get/set, realtime priority, affinity get/set, and `lwp_kill`.

No direct VFS implementation, but LWP ids appear in tracing and kinfo records.
