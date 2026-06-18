# File Research: sources/os/linux/linux/fs/exfat/super.c

Read status: complete, 943 lines.

This file implements the exFAT filesystem superblock, mount, remount, shutdown, and module lifecycle path. It owns `fs_context` option parsing, validates the on-disk exFAT boot region, initializes the in-memory `exfat_sb_info`, sets up the root inode, and registers the `exfat` filesystem type.

Key responsibilities:
- Mount option handling for uid/gid, masks, `allow_utime`, `iocharset`, `errors=`, `discard`, `keep_last_dots`, `sys_tz`, `time_offset`, and `zero_size_dir`.
- Boot sector validation: signature, `fs_name`, zeroed FAT compatibility field, FAT count, sector/cluster sizing, FAT/data layout consistency, volume flags, and boot checksum region.
- Superblock operations: inode allocation/free, inode write/eviction hooks, `statfs`, `show_options`, `put_super`, and shutdown.
- Root directory setup through `exfat_read_root()`, including root chain initialization, link count from directory entries, mode ownership mapping, timestamp initialization, and directory operations.
- NLS setup for non-UTF-8 mounts and UTF-8 dentry operation selection.
- Forced shutdown behavior via `exfat_force_shutdown()`, including freeze/thaw for sync shutdown modes and disabling discard after shutdown.
- Module init/exit: exFAT cache initialization, inode slab cache creation, filesystem registration, RCU-delayed superblock teardown, NLS unload, and upcase table freeing.

Important data/control flow:
- `exfat_init_fs_context()` allocates and defaults `exfat_sb_info`; `exfat_parse_param()` mutates its mount options.
- `exfat_get_tree()` calls `get_tree_bdev()` with `exfat_fill_super()`.
- `exfat_fill_super()` applies mount defaults, checks discard support, installs superblock operations, calls `__exfat_fill_super()`, initializes hashing/NLS, creates the root inode, and attaches `sb->s_root`.
- `__exfat_fill_super()` reads and verifies the boot sector/region, counts root clusters, loads upcase table and allocation bitmap, repairs the root cluster bitmap bit if needed, and counts used clusters.
- `exfat_reconfigure()` allows only limited dynamic remount changes; cached inode/dentry-affecting options are rejected if changed.

Concurrency and safety:
- `sbi->s_lock` protects volume dirty flag transitions around unmount/remount cleanup.
- RCU is used in `exfat_kill_sb()` to delay `sbi` freeing until readers are gone.
- Boot block writes use dirty buffer marking plus `REQ_SYNC | REQ_FUA | REQ_PREFLUSH` when changing volume flags.
- Mount-time validation is defensive against malformed sector sizes, FAT/data overlap, bad checksum, and impossible cluster geometry.

External dependencies:
- Uses Linux VFS `fs_context`, block device mount helpers, buffer heads, NLS, slab caches, RCU, and statfs APIs.
- Relies on other exFAT implementation files for FAT/cache/bitmap/upcase/inode/dentry operations declared in `exfat_fs.h`.

Research notes:
- This is the central exFAT integration file rather than the allocator or directory implementation.
- Error policy defaults to remount-ro and is exposed in mount option display.
- Persistent volume flags preserve dirty/media-failure bits across updates.
