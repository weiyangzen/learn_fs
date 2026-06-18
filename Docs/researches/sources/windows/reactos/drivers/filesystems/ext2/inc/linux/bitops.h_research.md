# File Research: sources/windows/reactos/drivers/filesystems/ext2/inc/linux/bitops.h

This header provides generic Linux-style bit manipulation helpers.

Key definitions:
- Kernel-only bit geometry macros: `BIT`, `BIT_MASK`, `BIT_WORD`, `BITS_TO_LONGS`, `BITS_PER_BYTE`.
- Search helpers: `find_first_zero_bit`, external `find_next_zero_bit`, `__ffs`, `find_first_bit`, `ffz`, `ffs`, `fls`, `fls64`, `fls_long`.
- Iteration macro: `for_each_bit`.
- Order helpers: `get_bitmask_order`, `get_count_order`.
- Rotation helpers: `rol32`, `ror32`.
- Hamming weight helpers: `hweight32`, `hweight64`, `hweight_long`.

Role:
- Supports bitmap scanning, allocation logic, log2 calculations, ext group bitmap handling, and journal bit state helpers.

Notable constraints:
- `find_next_bit` is referenced by `for_each_bit` but not declared in this header.
- The implementation assumes `BITS_PER_LONG`, endian-sized integer typedefs, and some generic macros are supplied by included compatibility headers.
