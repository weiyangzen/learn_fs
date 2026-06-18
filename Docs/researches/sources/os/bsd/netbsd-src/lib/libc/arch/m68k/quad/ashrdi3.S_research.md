# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/quad/ashrdi3.S

This file implements `__ashrdi3`, the signed 64-bit arithmetic right-shift helper for m68k. It shifts the high and low 32-bit halves across `%d0/%d1`, sign-extends the high word for shifts of 32 bits or more, and preserves temporary data registers.

It is used by compiler-generated signed `long long` shifts. The important behavior is sign propagation via arithmetic shifts and `smi/extbl`, which distinguishes it from the logical right-shift helper.
