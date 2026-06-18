# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/tst_types.c

Simple ABI sanity test for `ext2fs/ext2_types.h`. It verifies signed and unsigned fixed-width ext2 types have expected sizes: 8-bit types are 1 byte, 16-bit types 2 bytes, 32-bit types 4 bytes, and 64-bit types 8 bytes.

On mismatch it prints the offending type size and exits nonzero; on success it prints that the ext2 types are correct.
