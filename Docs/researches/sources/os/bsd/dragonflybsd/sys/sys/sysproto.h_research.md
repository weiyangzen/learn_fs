# File Research: sources/os/bsd/dragonflybsd/sys/sys/sysproto.h

Generated kernel syscall argument structs and handler prototypes.

Key responsibilities:
- Rejects userland inclusion.
- Includes syscall argument dependencies such as select, signal, ACL, cpumask, mqueue, msgport, and procctl headers.
- Defines `PAD_(t)` to pad each argument field to `register_t` alignment/size.
- Defines one `struct <syscall>_args` for each generated syscall argument layout.
- Declares kernel syscall handlers:
  - `int sys_<name>(struct sysmsg *, const struct <name>_args *)`

Covered syscall families:
- Classic process/file syscalls: `fork`, `read`, `write`, `open`, `close`, `wait4`, `execve`, `chdir`, `chmod`, `chown`.
- VFS/stat/mount syscalls: `mount`, `statfs`, `getfh`, `stat`, `fstat`, `lstat`, `statvfs`, `getvfsstat`.
- Socket syscalls: `socket`, `bind`, `connect`, `accept`, `sendmsg`, `recvmsg`, `accept4`.
- VM syscalls: `mmap`, `munmap`, `mprotect`, `madvise`, `mlock`, `vmspace_*`.
- IPC/POSIX realtime: SysV IPC, AIO, message queues, clocks, nanosleep.
- Signals/scheduling/LWP: `sigaction`, `sigprocmask`, `sched_*`, `lwp_*`, affinity calls.
- Modern namespace APIs: `openat`, `fstatat`, `unlinkat`, `utimensat`, `fexecve`, `posix_fallocate`.

Important invariants:
- Generated from `syscalls.master`; manual edits are not durable.
- Padding fields preserve architecture syscall argument ABI layout.
- Old compatibility names appear in places, e.g. `__getrlimit_args` and `__setrlimit_args`.
- Prototypes use the `struct sysmsg` first argument uniformly.

Research notes:
- This is the authoritative generated contract between trap/syscall dispatch and implementation functions.
- It pairs directly with `sysunion.h`, `sysmsg.h`, and `sysent.h`.
