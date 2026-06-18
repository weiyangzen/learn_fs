# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/riscv/Makefile.inc

This make include configures RISC-V libc architecture sources. It adds `__sigtramp2.S`, includes the architecture directory, and conditionally includes softfloat support when `MKSOFTFLOAT` is enabled.

There are no local string or stdlib additions here. It is straightforward architecture source-selection metadata.
