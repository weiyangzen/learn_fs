# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/mips/sys/compat_Ovfork.S

Implements MIPS legacy `vfork`. It invokes the `vfork` syscall and uses the MIPS convention where `v1` distinguishes parent from child.

On success, child returns zero while parent returns the child pid in `v0`; on error it tail-calls `__cerror`.

This is process-control ABI compatibility, used by old binaries including filesystem tools.
