# File Research: sources/os/bsd/dragonflybsd/sys/vfs/ext2fs/ext2_inode_cnv.c

This file converts between little-endian on-disk ext2 dinodes and DragonFlyBSD in-core `struct inode` fields, including extended timestamps, high UID/GID, huge-file block counts, flags, extents, and inode checksums.

Key responsibilities:
- Validate inode numbers, root inode type/link count, and extended inode size.
- Decode on-disk mode, link count, size, timestamps, flags, block counts, generation, ownership, EA block, and block pointers.
- Encode in-core inode state back to on-disk little-endian dinode fields.
- Translate ext2 append/immutable/nodump/index/extents flags to internal flags and back.
- Verify and set inode checksums.

Important functions:
- `ext2_decode_extra_time`: Adds high epoch bits and extracts nanoseconds from ext3 extra timestamp fields.
- `ext2_ei2i`: Converts disk inode to memory inode and calls `ext2_ei_csum_verify`.
- `ext2_encode_extra_time`: Packs epoch/nanosecond data for extra timestamp fields.
- `ext2_i2ei`: Converts memory inode to disk inode and calls `ext2_ei_csum_set`.
- `ext2_print_inode`: Optional debug printer under `EXT2FS_PRINT_EXTENTS`.

Important interactions:
- Called by inode loading code outside this group and by `ext2_update`.
- Uses definitions from `ext2_dinode.h` and checksum helpers from `ext2_csum.c`.

Notable behavior and risks:
- If link count is zero, `i_mode` is set to zero to mark the inode unused.
- Regular file size uses `e2di_size_high`; non-regular files do not.
- Huge-file accounting may convert block counts between filesystem blocks and disk blocks depending on `EXT4_HUGE_FILE`.
- The write path sets `e2di_dtime` based on link count and mtime.
