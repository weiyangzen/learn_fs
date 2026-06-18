# File Research: sources/os/bsd/netbsd-src/lib/libc/libcincludes.mk

Read completely: 20 lines.

This makefile fragment selects the libc architecture include directory. It derives `LIBC_MACHINE_ARCH` and `LIBC_MACHINE_CPU`, checks for an architecture `SYS.h`, sets `ARCHSUBDIR`, and then defines `ARCHDIR`.

Important interactions: included by build pieces that need libc's architecture-specific include tree. It prefers `${MACHINE_ARCH}` over `${MACHINE_CPU}` when both have a `SYS.h`.

Security/reliability notes: no runtime behavior. Build failure is explicit through a `.BEGIN` target if no matching architecture directory exists.
