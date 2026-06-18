# File Research: sources/os/bsd/dragonflybsd/sys/sys/syscall.h

Generated DragonFly system-call number table.

Key contents:
- Defines `SYS_*` numeric syscall IDs from `SYS_syscall` `0` through `SYS_futimesat` `555`.
- Defines `SYS_MAXSYSCALL` as `556`.
- Preserves obsolete/reserved slots as comments, keeping ABI numbering stable.
- Covers core process, VFS, sockets, IPC, POSIX realtime, kqueue, modules, jail, TLS, LWP, `*at`, message queue, affinity, random, and modern exec/sync calls.

Important behavior:
- The file is generated from `syscalls.master`; manual edits would be overwritten by `make sysent`.
- Numeric holes are intentional ABI compatibility slots.
- Consumers pair this with `sysproto.h`, `sysunion.h`, `syscall.mk`, and the kernel `sysent` table.

Research notes:
- This is ABI, not logic. Any renumbering would break user/kernel syscall compatibility.
