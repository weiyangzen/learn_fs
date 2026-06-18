# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/tst_byteswap.c

Small test program for `ext2fs_swab16` and `ext2fs_swab32`. It defines input/output pairs, checks both forward and reverse swaps, prints each conversion, counts errors, and returns the error count.

It covers representative values including single-bit, patterned, high-bit, and zero cases.
