# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/m68k/sys/compat_sigsuspend.S

Implements m68k compatibility `sigsuspend` for old integer signal sets. It emits the standard compatibility warning.

The wrapper dereferences the caller’s mask pointer into the syscall argument slot, invokes `compat_13_sigsuspend13`, and normally reports errors through `CERROR`; a successful return is marked as unexpected and returns zero.

This bridges modern pointer-style libc arguments to the legacy mask syscall ABI.
