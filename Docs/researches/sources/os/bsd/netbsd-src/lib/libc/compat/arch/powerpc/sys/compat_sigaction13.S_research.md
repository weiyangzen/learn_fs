# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/powerpc/sys/compat_sigaction13.S

Defines PowerPC compatibility `sigaction`.

It warns callers to include `<signal.h>` and maps `sigaction` to `compat_13_sigaction13`.

This is a minimal signal ABI veneer.
