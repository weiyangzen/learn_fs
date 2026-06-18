# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/riscv/gdtoa/Makefile.inc

This make include adds RISC-V gdtoa sources `strtof.c`, `strtold_pQ.c`, and `strtopQ.c`. That means the port builds both single-precision and quad/long-double parsing support.

There is no conditional logic in this file. It assumes the RISC-V libc ABI uses the relevant long-double conversion support.
