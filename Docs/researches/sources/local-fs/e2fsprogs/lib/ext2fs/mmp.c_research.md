# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/mmp.c

Implements ext4 multiple mount protection helpers. When `CONFIG_MMP` is enabled, it reads and writes the MMP block, initializes it, starts/stops ownership, and periodically updates the fsck sequence.

Reads use a separate file descriptor and `O_DIRECT` when suitable to avoid stale cached MMP data. Checks include block range validation, checksum verification unless ignored, magic validation, endian swapping, and aligned buffer allocation based on direct I/O requirements.

`ext2fs_mmp_start()` performs the protection handshake: read current sequence, wait if another sequence is active, verify it did not change, write a fresh random sequence, wait again, verify ownership, then write `EXT4_MMP_SEQ_FSCK`.

`ext2fs_mmp_stop()` and `ext2fs_mmp_update2()` compare the saved buffer with freshly read disk state before writing. A mismatch returns `EXT2_ET_MMP_CHANGE_ABORT`, signaling that pending filesystem modifications should be abandoned.
