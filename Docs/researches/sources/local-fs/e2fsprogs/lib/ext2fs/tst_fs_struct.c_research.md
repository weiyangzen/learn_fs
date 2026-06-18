# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/tst_fs_struct.c

Prints field offsets and sizes for `struct struct_ext2_filsys`. It is a layout inspection tool rather than a strict validator: if padding exists between fields, it prints a padding note and continues.

Under GCC 4 or newer, it lists offsets for core filesystem context fields including I/O channel, flags, superblock, group descriptors, bitmaps, callbacks, badblocks, dblist, image fields, allocation hooks, MMP state, cache, and private data.
