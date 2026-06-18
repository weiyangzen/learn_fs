# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/mips/sys/getcontext.S

This file implements `_getcontext` and weak alias `getcontext`. After a successful kernel `getcontext`, it forces the saved `v0` return register in the ucontext to zero and stores the current return address as the saved EPC; for non-o32 it also stores the saved GP from PIC setup.

It uses offsets from `assym.h` and `<machine/mcontext.h>`. The wrapper is required so a later `setcontext` resumes as if `getcontext` returned zero.
