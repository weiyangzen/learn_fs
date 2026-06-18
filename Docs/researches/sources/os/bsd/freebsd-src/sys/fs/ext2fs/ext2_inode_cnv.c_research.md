# File Research: sources/os/bsd/freebsd-src/sys/fs/ext2fs/ext2_inode_cnv.c

This file converts ext2/ext3/ext4 on-disk inodes to FreeBSD in-memory `struct inode` objects and back.

Key responsibilities:
- Validate inode numbers, root inode structure, and extra inode size.
- Decode mode, link count, size, timestamps, flags, block counts, xattr block pointers, generation, UID/GID, device numbers, and block/extent pointers.
- Decode ext4 extra timestamp epoch/nanosecond fields and birth time.
- Encode FreeBSD inode state back to little-endian disk format.
- Encode large block counts with `EXT4_HUGE_FILE` when needed.
- Preserve extent root bytes when `IN_E4EXTENTS` is set.
- Verify and set inode metadata checksums.

Important functions:
- `ext2_print_inode`: Optional debug printer under `EXT2FS_PRINT_EXTENTS`.
- `ext2_old_valid_dev`, `ext2_old_encode_dev`, `ext2_old_decode_dev`, `ext2_new_encode_dev`, `ext2_new_decode_dev`: Device number format conversion.
- `ext2_decode_extra_time`, `ext2_encode_extra_time`: ext4 timestamp extension conversion.
- `ext2_ei2i`: Disk-to-memory inode conversion and checksum verification.
- `ext2_i2ei`: Memory-to-disk inode conversion and checksum update.

Important interactions:
- Called by inode read/update paths and `ext2_update`.
- Uses constants from `ext2_dinode.h` and checksum helpers from `ext2_csum.c`.
- Maps disk flags to FreeBSD `SF_APPEND`, `SF_IMMUTABLE`, `UF_NODUMP`, `IN_E3INDEX`, and `IN_E4EXTENTS`.

Notable behavior:
- Zero-link disk inodes are exposed with `i_mode = 0`.
- Regular files can use high size bits; non-regular files do not.
- Huge-file block count encoding depends on filesystem feature support.
