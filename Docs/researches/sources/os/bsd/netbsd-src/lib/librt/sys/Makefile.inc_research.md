# File Research: sources/os/bsd/netbsd-src/lib/librt/sys/Makefile.inc

Read completely: 25 lines.

Generates architecture-specific syscall assembly stubs for AIO, message queue, processor-set, and `_pset_bind` functions. It adds `${.CURDIR}/sys` and `${ARCHDIR}/sys` to `.PATH`, appends generated assembly names to `SRCS`, and removes them during clean.

Generated stubs include `SYS.h` and invoke `RSYSCALL(${.PREFIX})`. The file also adds `cerror.S`, remaps `__cerror` to `__rt_cerror`, includes the libc object directory, and defines `_REENTRANT`.
