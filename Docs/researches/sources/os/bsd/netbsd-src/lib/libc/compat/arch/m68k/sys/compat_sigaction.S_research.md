# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/m68k/sys/compat_sigaction.S

Defines m68k compatibility `sigaction`. The file warns old references to include `<signal.h>` for correct symbol selection.

It uses `PSEUDO(sigaction, compat_13_sigaction13)`, preserving the NetBSD 1.3 signal-action ABI.

Filesystem relevance is indirect: signal handling affects all old binaries, including filesystem utilities.
