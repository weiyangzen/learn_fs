# File Research: sources/os/plan9/9front/sys/src/9/sgi/fptrap.c

Handles selected MIPS floating-point traps, especially unimplemented operations that are likely underflows. `fptrap` inspects FCR31, fetches the trapping instruction, attempts `fpunimp`, advances PC, and clears the unimplemented bit when handled.

`fpunimp` decodes COP1 operations and formats, estimates exponents/signs, handles ABS/NEG directly, and zeroes destination registers for guessed underflow cases while setting underflow exception/sticky bits. It does not implement full FP emulation.

`branch` decodes integer and FP branch/jump instructions to compute the correct resume PC when the FP trap occurred in a branch delay slot.
