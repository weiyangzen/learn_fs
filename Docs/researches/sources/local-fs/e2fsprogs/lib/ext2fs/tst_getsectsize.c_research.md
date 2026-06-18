# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/tst_getsectsize.c

Command-line test utility for sector-size and direct-I/O alignment probing. It requires a device path, calls `ext2fs_get_device_sectsize` for logical sector size and `ext2fs_get_device_phys_sectsize` for physical sector size, then opens the device read-only and prints `ext2fs_get_dio_alignment(fd)`.

Errors from ext2fs helpers are reported through `com_err`; open failures use `perror`.
