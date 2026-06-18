# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/mips/sys/compat___sigreturn14.S

Defines MIPS `__sigreturn14` as a compatibility wrapper to `compat_16___sigreturn14`.

The file emphasizes preserving user register state during signal return and uses the `PSEUDO` syscall macro.

This supports old signal trampoline paths and legacy binaries.
