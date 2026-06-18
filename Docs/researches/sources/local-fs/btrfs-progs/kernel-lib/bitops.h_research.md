# File Research: sources/local-fs/btrfs-progs/kernel-lib/bitops.h

## Purpose
Userspace bit operation helpers modeled after Linux/perf code.

## Key Interfaces
- Bitmap sizing and indexing macros: `BITS_TO_LONGS`, `BITS_TO_U64`, `BIT_MASK`, `BIT_WORD`.
- Iteration macros: `for_each_set_bit`, `for_each_set_bit_from`.
- Bit mutation/test helpers: `set_bit`, `clear_bit`, `test_and_set_bit`.
- Hamming weight helpers: `hweight32`, `hweight64`, `hweight_long`.
- Search helpers: `__ffs`, `ffz`, `_find_next_bit`, `find_next_bit`, `find_next_zero_bit`, first-bit aliases.
- Little-endian bit scanning helpers, with byte-swapped implementations for big-endian hosts.

## Dependencies
Includes `kerncompat.h`, `<endian.h>`, and `common/internal.h` for common types/macros such as `round_down`, `min`, and endian utilities.

## Notable Behaviors
- Bit searches return `size`/`nbits` when no matching bit exists.
- `_find_next_bit()` optionally intersects `addr1` and `addr2`, though this file only exposes public wrappers for the single-address cases.
- Big-endian `_le` functions use `ext2_swab()` to emulate little-endian bitmap numbering.

## Risks
- Helpers are non-atomic despite kernel-like names; suitable for userspace single-threaded or externally synchronized use.
- `__ffs()` is undefined for zero input by contract; callers must guard.
