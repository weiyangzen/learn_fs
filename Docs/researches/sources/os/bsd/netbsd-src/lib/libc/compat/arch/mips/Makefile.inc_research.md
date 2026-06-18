# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/mips/Makefile.inc

Build include fragment for MIPS libc compatibility code.

It includes the architecture-specific `gen/Makefile.inc` and `sys/Makefile.inc` fragments through `${COMPATARCHDIR}`.

No source behavior is defined here; it only wires MIPS compatibility objects into the libc build.
