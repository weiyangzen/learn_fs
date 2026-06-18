# File Research: sources/os/bsd/dragonflybsd/sys/sys/sysunion.h

Generated union of all syscall argument structs.

Key contents:
- Kernel-only generated header.
- Includes `sys/sysproto.h`.
- Defines `union sysunion` with one member per generated syscall argument struct.
- Member names correspond to syscall names, including `__sysctl`, `__getcwd`, `vmspace_*`, `lwp_*`, `mq_*`, `*at`, and modern additions.

Important behavior:
- Used by `struct sysmsg` as `extargs` for syscalls needing more than the register argument path can carry.
- Must remain layout-compatible with generated syscall argument structs.
- Generated from `syscalls.master`; manual edits are not durable.

Research notes:
- This is a space-efficient carrier for syscall argument alternatives.
- It is tightly coupled to `sysproto.h` and `sysmsg.h`.
