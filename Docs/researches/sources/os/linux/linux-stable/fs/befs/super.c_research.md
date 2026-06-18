# File Research: sources/os/linux/linux-stable/fs/befs/super.c

This file loads and validates BeFS superblock metadata.

Exports:
- `befs_load_sb()` copies the packed on-disk superblock into `struct befs_sb_info` in host byte order.
- `befs_check_sb()` validates magic numbers, block size, shift consistency, allocation-group shift consistency, and clean journal state.

Load behavior:
- Determines byte order from `fs_byte_order`.
- Converts magic fields, block geometry, counts, inode size, allocation group fields, flags, journal fields, root directory, and indices addresses.
- Initializes `nls` to `NULL`.

Validation behavior:
- Requires all three magic values.
- Allows block sizes 1024, 2048, 4096, or 8192.
- Rejects block sizes larger than `PAGE_SIZE`.
- Requires `1 << block_shift == block_size`.
- Logs but does not reject mismatch between `ag_shift` and `blocks_per_ag`.
- Rejects dirty filesystems or nonempty journal ranges.

Integration:
- Called from `befs_fill_super()` in `linuxvfs.c`.
- Depends on endian helpers and BeFS superblock types.

Risk notes:
- If `fs_byte_order` is neither native LE nor BE marker, `byte_order` is not explicitly initialized here before conversions.
- Dirty/journaled volumes are rejected; no journal replay exists.
