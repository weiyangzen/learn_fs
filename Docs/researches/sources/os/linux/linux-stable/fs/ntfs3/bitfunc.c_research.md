# File Research: sources/os/linux/linux-stable/fs/ntfs3/bitfunc.c

This file implements two low-level bitmap predicates for ntfs3.

Main responsibilities:
- Checks whether every bit in `[bit, bit + nbits)` is clear.
- Checks whether every bit in `[bit, bit + nbits)` is set.
- Handles unaligned bit offsets and then scans byte/word-aligned regions efficiently.

Important functions and data:
- `fill_mask[]` and `zero_mask[]` provide first-N-bit and after-N-bit masks for partial bytes.
- `are_bits_clear()` returns true only if the selected range contains no set bits.
- `are_bits_set()` returns true only if the selected range contains all set bits.
- `BITS_IN_SIZE_T` lets the implementation scan native word chunks after alignment.

Research notes:
- These helpers are used by the ntfs3 bitmap allocator to verify free/used ranges in on-disk bitmap buffers.
- The code treats zero-length ranges as true in the initial partial-byte cases.
