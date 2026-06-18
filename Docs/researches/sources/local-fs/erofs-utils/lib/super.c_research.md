# File Research: sources/local-fs/erofs-utils/lib/super.c

## Scope

This file implements EROFS superblock read, validation, teardown, mkfs reservation/writing, checksum handling, device-table handling, and clean/incremental mkfs filesystem initialization.

## Public And Internal APIs Covered

- Read-side lifecycle: `erofs_read_superblock()` and `erofs_put_super()`.
- Write-side lifecycle: `erofs_reserve_sb()`, `erofs_writesb()`, `erofs_mkfs_format_fs()`, and `erofs_mkfs_load_fs()`.
- Checksum helpers: `erofs_enable_sb_chksum()` and `erofs_superblock_csum_verify()`.
- Device table helpers: `erofs_mkfs_init_devices()` and `erofs_write_device_table()`.
- Internal validation/setup: `check_layout_compatibility()` and `erofs_init_devices()`.

## Control Flow And Behavior

- `erofs_read_superblock()` reads the first maximum block, verifies magic, block size, incompatible feature bits, extended superblock size, root nid encoding, optional metabox nid, inode count, checksum fields, timestamps, UUID, shared-xattr prefix constraints, compression config, device table, and xattr prefixes before setting `sbi->sb_valid`.
- Feature compatibility is fail-closed: unknown incompatible bits are rejected against `EROFS_ALL_FEATURE_INCOMPAT`.
- Device-table reads compare user-provided extra-device count with on-disk count when both exist, allocate `sbi->devs`, copy tags and block counts, compute `device_id_mask`, and accumulate `total_blocks`.
- `erofs_put_super()` frees extra-device paths, tears down the buffer manager, compression state, and xattr state, then clears `sb_valid`.
- `erofs_writesb()` materializes an on-disk `struct erofs_super_block`, including 48-bit block/root fields when needed, optional compression config, optional metabox nid, extra device metadata, UUID, volume name, and feature flags. It writes the superblock at the reserved buffer offset or device start.
- `erofs_reserve_sb()` pins the superblock as the first allocation by ballooning a metadata buffer to cover `EROFS_SUPER_OFFSET + sb_size` and asserting that `erofs_btell()` is zero.
- Superblock checksums are enabled by rereading the superblock area, setting the compat checksum feature, computing CRC32C with the checksum field included as zero before final assignment, and rewriting the same bytes.
- Clean mkfs initializes a new buffer manager and reserves the superblock. Incremental mkfs reads an existing superblock, estimates append start from image file size or current block count, then initializes the buffer manager from that start block.

## State And Data Structures

- Populates `erofs_sb_info` fields for feature flags, block size, superblock size, block counts, metadata and xattr block addresses, root and packed nids, metabox nid, inode count, timestamps, checksum, UUID, device table, and xattr prefixes.
- Uses `erofs_buffer_head` handles for reserved superblock and device-table regions.
- Device slots use on-disk `struct erofs_deviceslot` with low 32-bit block fields and fixed-size tags.

## Dependencies

- Depends on block/device I/O helpers, buffer-manager allocation and mapping, CRC32C, compression config parsing, compression teardown, metabox feature helpers, and xattr prefix initialization/cleanup.
- Shares feature-bit contracts with on-disk EROFS format definitions in public/internal headers.

## Risks And Invariants

- Unknown incompatible features, invalid block sizes, invalid extended superblock size, invalid metabox self-loop, and invalid shared-xattr prefix ids are corruption or compatibility boundaries.
- Device table count, slot offset, and block accumulation must match mkfs and mount/read behavior; mismatches are rejected.
- The superblock must stay pinned at image offset zero for mkfs output correctness.
- Checksum computation intentionally skips the first 1024 bytes when block size permits, preserving space for boot-sector oddities.
