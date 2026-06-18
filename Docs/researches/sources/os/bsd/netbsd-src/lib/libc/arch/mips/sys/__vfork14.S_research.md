# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/mips/sys/__vfork14.S

This file implements MIPS `__vfork14`. It loads the syscall number, executes `syscall`, routes errors to `__cerror`, and on success converts the kernel’s parent/child flag in `v1` into standard return values.

The parent receives the child PID in `v0`; the child returns zero. PIC setup and return are handled through the MIPS syscall macros.
