# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/riscv/sys/getcontext.S

This file implements `_getcontext` with weak alias `getcontext`. It saves the ucontext pointer, calls the kernel `getcontext`, then stores zero into the saved return-value slot and `ra` into the saved PC slot.

The offsets come from `assym.h`. This ensures a restored context resumes as though `getcontext` returned successfully with zero.
