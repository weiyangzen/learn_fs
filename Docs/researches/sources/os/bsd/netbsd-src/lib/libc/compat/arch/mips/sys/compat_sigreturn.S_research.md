# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/mips/sys/compat_sigreturn.S

Defines MIPS compatibility `sigreturn`.

It warns for old references and maps `sigreturn` to `compat_13_sigreturn13`.

The file is a syscall veneer, with comments noting register state preservation requirements.
