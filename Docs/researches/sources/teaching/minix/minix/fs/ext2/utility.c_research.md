# File Research: sources/teaching/minix/minix/fs/ext2/utility.c

This file provides ext2 utility routines for buffers, endian conversion, string comparison, and bitmap operations.

Key functions:
- `get_block(dev, block, how)`: wrapper around `lmfs_get_block` that panics on real I/O errors and returns `NULL` only for failed `PEEK`.
- `conv2(norm, w)` / `conv4(norm, x)`: endian conversion helpers.
- `ansi_strcmp(ansi_s, s2, ansi_s_length)`: compares fixed-length directory names with C strings.
- `setbit(bitmap, max_bits, word)`: finds and sets a free bit starting at a bitmap word.
- `setbyte(bitmap, max_bits)`: finds and sets a fully free byte for preallocation.
- `unsetbit(bitmap, bit)`: clears a set bit and reports if it was already clear.

Role:
- Shared low-level support for block/inode allocation, directory lookup, and disk structure conversion.

Notable bug:
- `setbyte()` tests `if (*wptr | 0)` which is equivalent to `if (*wptr)`, so it works as a nonzero test but is likely intended to be clearer.
