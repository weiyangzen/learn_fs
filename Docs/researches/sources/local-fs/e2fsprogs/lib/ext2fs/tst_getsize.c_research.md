# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/tst_getsize.c

Command-line test for `ext2fs_get_device_size2`. It takes a device path, initializes the ext2 error table, requests the size in 1024-byte blocks, prints the resulting block count, and exits nonzero on errors.
