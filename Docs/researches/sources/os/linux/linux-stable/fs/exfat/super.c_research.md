# File Research: sources/os/linux/linux-stable/fs/exfat/super.c

## Summary
Implements the Linux exFAT superblock, mount-context, boot-region validation, root inode setup, mount option parsing, shutdown, and module registration paths.

## Main Responsibilities
- Parses exFAT mount parameters through the modern `fs_context` API.
- Reads and validates the exFAT boot sector and boot checksum region.
- Initializes per-superblock state, allocation bitmap, upcase table, inode hash table, root inode, and NLS conversion.
- Maintains volume dirty/media-failure flags in the boot sector.
- Handles statfs, remount/reconfigure, forced shutdown, superblock teardown, and inode slab lifecycle.

## Key APIs
- `exfat_init_fs_context()`, `exfat_parse_param()`, `exfat_get_tree()`, `exfat_reconfigure()`.
- `exfat_fill_super()`, `__exfat_fill_super()`.
- `exfat_read_boot_sector()`, `exfat_verify_boot_region()`.
- `exfat_set_volume_dirty()`, `exfat_clear_volume_dirty()`, `exfat_force_shutdown()`.
- `exfat_alloc_inode()`, `exfat_free_inode()`, `exfat_kill_sb()`.

## Important Behavior
Mount validation checks boot signature, filesystem name, zeroed FAT-compatible fields, FAT count, sector/cluster geometry, FAT length, data start, boot-region signatures, and checksum sectors. The root directory chain is counted before loading upcase/bitmap entries to avoid infinite traversal on corrupt media.

`exfat_fill_super()` sets `SB_NODIRATIME`, timestamp limits, max file size, dentry operations, NLS state, root inode metadata, inode hash insertion, and the root dentry. Remount only allows dynamic changes for options that are not cached into inodes or dentries; charset, uid/gid, masks, time interpretation, and name handling are rejected if changed.

## State and Lifetime
`struct exfat_sb_info` is allocated per mount context. On mount failure, bitmap and boot-sector buffers are released on the relevant error paths. On kill, `kill_block_super()` runs first and the remaining exFAT superblock state is freed after RCU, including NLS, upcase table, iocharset, and `sbi`.

## Risks
Boot geometry and checksum validation are central corruption gates. Volume flag writes bypass changes on read-only mounts but otherwise synchronously update the boot sector with flush/FUA semantics. Remount swaps option structs, so rejected cached options must stay rejected to avoid stale dentry/inode interpretation.
