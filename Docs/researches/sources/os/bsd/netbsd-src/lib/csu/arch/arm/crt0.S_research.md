# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/arm/crt0.S

ARM process entry stub. It rearranges NetBSD entry registers so `r0` becomes cleanup and `r1` becomes `ps_strings`.

Before branching to `___start`, it aligns the stack to an 8-byte boundary with `bic sp, sp, #7`.
