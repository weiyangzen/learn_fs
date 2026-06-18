# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/tst_inode_size.c

Validates the layout of `struct ext2_inode_large`. For GCC 4 or newer, it checks expected field sizes and exact offsets for the classic 128-byte inode portion plus large-inode extension fields.

It exits immediately on size or offset mismatches. Covered fields include mode/uid/gid/timestamps, blocks, flags, Linux OS-dependent fields, checksum fields, extra timestamps, creation time, high version, and project ID.
