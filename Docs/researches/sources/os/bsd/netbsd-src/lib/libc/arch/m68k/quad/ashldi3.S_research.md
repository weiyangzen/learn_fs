# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/quad/ashldi3.S

This file implements `__ashldi3`, the 64-bit arithmetic left-shift helper for m68k. It loads a 64-bit value as high word in `%d0` and low word in `%d1`, handles shifts below and above 32 bits, combines cross-word bits, clears the low half when needed, and restores scratch registers before returning.

It is compiler runtime glue for targets where 64-bit shifts require helper calls. Correctness depends on the m68k calling convention, callee-saved scratch preservation through `moveml`, and the assumption that the shift count is in the valid compiler-generated range.
