# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/sys/Makefile.inc

Read completely: 23 lines.

This makefile fragment lists the syscall compatibility source files built into libc, covering directory entries, time32/time50 wrappers, stat/statfs/statvfs transitions, file handles, sockets, SysV IPC, timers, scheduling, `dup3`, kqueue, message queues, and signal trampolines. It also adds the `getdirentries.3` man page and lint stub.

Security/reliability notes: build orchestration only, but it defines which old ABI symbols are actually present.
