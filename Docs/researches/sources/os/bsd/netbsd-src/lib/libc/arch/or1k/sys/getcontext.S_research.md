# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/or1k/sys/getcontext.S

This file implements `_getcontext` with weak alias `getcontext`. It calls the kernel `getcontext` syscall, then stores the current link register into the saved PC slot and stores zero into the saved return-value register slot.

The offsets come from `assym.h`. This ensures that resuming the captured context behaves as if `getcontext` returned zero.
