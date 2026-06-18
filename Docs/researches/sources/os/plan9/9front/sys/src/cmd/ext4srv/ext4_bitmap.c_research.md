# File Research: sources/os/plan9/9front/sys/src/cmd/ext4srv/ext4_bitmap.c

Small bitmap utility implementation used by block and inode allocation code.

Key behavior:
- `ext4_bmap_bits_free` clears a range of bitmap bits, optimizing byte-aligned middle ranges with `memset`.
- `ext4_bmap_bit_find_clr` scans a bitmap range for the first clear bit, first aligning to a byte boundary, then scanning whole bytes, then the tail bits.
- Reports no-space through both return value `-1` and `*no_space = true`.

Notable dependencies:
- Inline bit operations such as `ext4_bmap_bit_clr`, `ext4_bmap_bit_set`, and `ext4_bmap_is_bit_clr` come from headers.

Research notes:
- The helpers assume caller-provided range bounds are valid for the bitmap buffer.
- `ext4_bmap_bits_free` clears tail bits using bit indexes relative to the advanced byte pointer, which matches the local bit helper convention.
