# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/riscv/sys/sbrk.S

This file implements `_sbrk` with weak alias `sbrk`. It loads `__curbrk`, adds the requested increment, saves the new break, calls kernel `break`, stores the new value on success, and returns the old break.

It is the RISC-V cached program-break wrapper. Like the other ports, it updates state only on successful kernel acceptance.
