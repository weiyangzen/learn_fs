# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/powerpc/sys/getcontext.S

This file implements `_getcontext` and weak `getcontext`. It saves the ucontext pointer, calls the kernel `getcontext`, stores the current LR into the saved PC slot, stores zero as the saved `%r3` return value, and returns.

It uses `assym.h` offsets such as `UC_GREGS_PC` and `UC_GREGS_R3`. This wrapper fixes the captured context so resuming it reports a successful `getcontext`.
