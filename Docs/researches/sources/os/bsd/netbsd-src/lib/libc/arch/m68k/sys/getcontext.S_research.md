# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/sys/getcontext.S

This file implements `_getcontext` with weak public alias `getcontext`. It calls the kernel `getcontext` syscall, then adjusts the saved user context so resuming it returns to the caller after the syscall wrapper with return value zero.

It updates `UC_MCONTEXT_SP`, `UC_MCONTEXT_PC`, and `UC_MCONTEXT_D0` using offsets from `assym.h`. This is sensitive to ucontext layout and m68k return-address conventions.
