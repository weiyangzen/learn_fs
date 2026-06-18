# File Research: sources/os/linux/linux-stable/fs/ntfs3/super.c

Purpose: Implements NTFS3 filesystem registration, fs_context mount option parsing, superblock initialization/teardown, boot-sector validation, sync/statfs/export operations, procfs volume reporting, discard, and module init/exit.

Key responsibilities:
- Provides ratelimited NTFS3 logging helpers under `CONFIG_PRINTK`.
- Shares identical `$UpCase` tables across mounts using a small global reference-counted table.
- Parses mount options including uid/gid/masks, immutable system files, discard, force, sparse, hidden/meta behavior, Windows-name rules, ACL, iocharset, prealloc, nocase, and delayed allocation.
- Handles remount/reconfigure constraints, including refusing rw remount when journal replay is needed or dirty volume is not forced, and disallowing iocharset changes.
- Creates `/proc/fs/ntfs3/<dev>/volinfo` and writable `label` entries when procfs is enabled.
- Allocates/frees NTFS inodes from `ntfs_inode_cachep`.
- Implements super operations: inode allocation/free, eviction, put_super, statfs, show_options, shutdown, sync_fs, and write_inode.
- Implements NFS export helpers through file handles and parent lookup.
- Validates boot-sector geometry and initializes core sizing in `ntfs_init_from_boot()`, including fallback to the alternative boot sector.
- Mounts in `ntfs_fill_super()` by loading `$Volume`, `$MFTMirr`, `$LogFile`, `$MFT`, `$Bitmap`, `$BadClus`, `$AttrDef`, `$UpCase`, optional NTFS 3.x metadata files, and root.
- Unmaps metadata buffer aliases and issues aligned discard requests.
- Registers/unregisters the `ntfs3` filesystem and initializes bitmap/inode caches.

Important invariants:
- Boot validation checks NTFS signature, sector/cluster sizing, MFT/MFTMirr LCNs, record/index size limits, cluster/media sector compatibility, raw-volume size, 32-bit cluster build limits, and derived maximum file sizes.
- Mount rw is blocked when log replay is required but failed, or when the volume is dirty without `force`.
- `$MFT` bitmap runs from extent records are merged before initializing the MFT bitmap window.
- `$Bitmap` size must cover all volume clusters.
- `$BadClus` real runs are counted and, on rw mounts, forced used in the allocation bitmap.
- `$AttrDef` must start with `ATTR_STD` and is parsed in increasing type order to cache EA and reparse maximum sizes.
- `$UpCase` must be exactly 0x10000 UTF-16 entries and is endian-swapped on big-endian builds.

Dependencies:
- Uses VFS fs_context, block-device, exportfs, NLS, procfs, seq_file, statfs, and module infrastructure.
- Drives initialization of nearly every NTFS3 subsystem declared in `ntfs_fs.h`.

Risk notes:
- Error cleanup is split between `ntfs3_put_sbi()`, `ntfs3_free_sbi()`, `ntfs_put_super()`, fs_context free, and kill_sb; ownership transfer in successful mount paths must remain exact.
- If the alternate boot sector is accepted on rw mount, primary boot may be rewritten after root creation.
- `ntfs_sync_fs()` clears the dirty flag only if metadata writes succeed, then updates MFTMirr and optionally flushes the block device.
