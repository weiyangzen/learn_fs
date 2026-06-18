# File Research: sources/local-fs/ocfs2-tools/libocfs2/bitops.c

Portable C bit operations for OCFS2 userspace bitmaps, adapted from e2fsprogs/ext2fs code.

Provides byte-addressed little-bit-order `ocfs2_set_bit`, `ocfs2_clear_bit`, and `ocfs2_test_bit`. Search helpers include first/next set bit and first/next clear bit over arbitrary bit counts, including non-byte-aligned final ranges. `ocfs2_get_bits_set()` counts set bits by repeatedly using next-set search.

The implementation uses `ffs()` and byte scanning rather than architecture assembly. Debug mode exercises boundary cases around the last bit in an arbitrary bitmap.
