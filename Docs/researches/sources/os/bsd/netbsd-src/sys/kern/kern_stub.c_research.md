# File Research: sources/os/bsd/netbsd-src/sys/kern/kern_stub.c

Read completely: 341 lines.

Provides fallback stubs, weak aliases, and generic error helpers for optional kernel facilities, unsupported syscalls, driver entry points, bus helpers, interrupt-distribution hooks, and architectures without kernel preemption.

Optional facility stubs:
- SYSV IPC entry points alias to `enosys` when non-modular kernels omit SYSV message queues, shared memory, or semaphores.
- Ktrace probes and syscalls alias to `nullop`, `sys_nosys`, or `enosys` when `KTRACE` is not configured.
- Device registration, SPL debug, machdep init, userconf, module MD init, kobj renamespace, interrupt query/distribution, bus-space reservation/tagging, bus-DMA tag creation, and kernel FPU hooks use weak aliases to no-op or error functions.
- Scheduler activation syscalls and selected compat stubs are hard-wired to `sys_nosys`.

Preemption stubs:
- When `__HAVE_PREEMPTION` is absent, `cpu_kpreempt_enter()` returns false, `cpu_kpreempt_exit()` is empty, and `cpu_kpreempt_disabled()` returns true.
- If preemption exists without `MULTIPROCESSOR`, the file triggers a build error.

Generic syscall/device helpers:
- `sys_nosys()` sends `SIGSYS` to the calling process under `proc_lock` and returns `ENOSYS`.
- `enodev()`, `enxio()`, `enoioctl()`, `enosys()`, and `eopnotsupp()` return their corresponding errno values.
- `voidop()`, `nullop()`, and `nullret()` provide common no-op callbacks.
- `default_bus_space_handle_is_equal()` and `default_bus_space_is_equal()` compare handles/tags with `memcmp()`.

Notes:
- This file is glue for build-time configurability; most symbols are intentionally replaceable by real implementations.
- The only active process side effect is `sys_nosys()` delivering `SIGSYS`.
