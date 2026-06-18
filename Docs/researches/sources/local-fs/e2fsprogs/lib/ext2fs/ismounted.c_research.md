# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/ismounted.c

Implements libext2fs mount/busy detection. The public entry points are `ext2fs_check_mount_point()` and `ext2fs_check_if_mounted()`, returning `EXT2_MF_MOUNTED`, `EXT2_MF_ISROOT`, `EXT2_MF_READONLY`, `EXT2_MF_SWAP`, `EXT2_MF_BUSY`, and `EXT2_MF_EXTFS`.

On Linux it first probes block devices with `open(O_RDONLY | O_EXCL)` to cheaply determine whether the device is busy. It then checks `/proc/swaps`, `/proc/mounts`, and configured mtab paths via `getmntent`, with extra handling for loop-mounted regular files by comparing loop backing inode/device metadata.

The root filesystem path receives special treatment because mount tables may report `/dev/root`; the code compares the candidate device number against `stat("/")` and probes writability by creating `/.ismount-test-file`.

Important behaviors: environment variables can force pretend mounted states for tests, missing mtab can be ignored via `EXT2FS_NO_MTAB_OK`, and non-Linux platforms use `getmntinfo` when available. String copies to `mtpt` use `strncpy` with caller-supplied length and may not NUL-terminate if the mount path exactly fills the buffer.
