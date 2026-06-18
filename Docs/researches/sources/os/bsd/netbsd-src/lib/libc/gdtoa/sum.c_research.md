# File Research: sources/os/bsd/netbsd-src/lib/libc/gdtoa/sum.c

Purpose: Adds two `Bigint` values.

Core behavior:
- Swaps operands so the longer `Bigint` drives output sizing.
- Allocates a result with the larger operand's capacity.
- Adds shared limbs with carry, then remaining high limbs.
- Supports both packed-32 and packed-16 limb modes.
- Grows the result if a final carry exceeds current capacity.

Dependencies:
- Includes `gdtoaimp.h`.
- Uses `Balloc`, `Bcopy`, `Bfree`, `Storeinc`, and packing macros.
