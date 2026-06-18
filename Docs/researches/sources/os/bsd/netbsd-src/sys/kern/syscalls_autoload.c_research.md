# File Research: sources/os/bsd/netbsd-src/sys/kern/syscalls_autoload.c

Generated syscall autoload table from `syscalls.master`, produced by `makesyscalls.sh`. It maps syscall numbers to kernel modules that should be autoloaded when optional or compatibility syscall implementations are needed.

Core content:
- `netbsd_syscalls_autoload[]`: array of `{ SYS_..., "module" }` entries terminated by `{ 0, NULL }`.

Major module groups:
- Compatibility modules: `compat_09`, `compat_12`, `compat_13`, `compat_16`, `compat_20`, `compat_30`, `compat_40`, `compat_43`, `compat_50`, `compat_60`, `compat_90`, `compat_100`, and SysV compatibility variants.
- Optional subsystem modules: `ptrace`, `nfsserver`, `lfs`, `openafs`, `sysv_ipc`, `ksem`, `mqueue`, and `aio`.
- Some entries are conditional on build options such as `_LP64`, `NTP`, and `_KERNEL_OPT`.

Relevant relationships:
- LFS syscalls map to `lfs`.
- AIO syscalls map to `aio`.
- POSIX message queues map to `mqueue`.
- SysV IPC and semaphore operations map to `sysv_ipc` or compatibility SysV modules.
- Compatibility select/poll/time/signal syscalls map to the corresponding compat modules.

Research notes:
- This file has no hand-written behavior, but it is part of syscall dispatch availability: missing optional implementations can be loaded on demand based on this table.
