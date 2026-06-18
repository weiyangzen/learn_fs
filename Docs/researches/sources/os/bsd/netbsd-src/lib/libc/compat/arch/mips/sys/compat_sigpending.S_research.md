# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/mips/sys/compat_sigpending.S

Implements MIPS compatibility `sigpending`.

After invoking `compat_13_sigpending13`, it stores the returned mask using `INT_S` at `_SC_ONSTACK(a0)` and returns zero. The use of `assym.h` supplies the sigcontext offset constant.

This is a legacy signal-mask adapter with architecture-specific storage semantics.
