# File Research: sources/os/linux/linux/fs/ntfs3/bitfunc.c

Read coverage: complete file, 128 lines.

This file provides optimized bit-range predicates over little-endian bitmap memory.

Key functions:
- `are_bits_clear(lmap, bit, nbits)` returns true if all bits in `[bit, bit + nbits)` are zero.
- `are_bits_set(lmap, bit, nbits)` returns true if all bits in `[bit, bit + nbits)` are one.
- Both handle unaligned starting bits, byte-alignment cleanup, native `size_t` chunks, trailing bytes, and final partial bits.

Integration:
- Used by ntfs3 bitmap window code to validate free/used cluster ranges from on-disk bitmap buffers.
- Depends on `MINUS_ONE_T` from ntfs3 headers for full-word comparison.

Risks:
- Reads native `size_t *` from byte buffers after manual alignment. The alignment code is central to avoiding unaligned access issues.
- Endianness is safe for all-zeros/all-ones checks but these helpers are not general bit-order scanners.
