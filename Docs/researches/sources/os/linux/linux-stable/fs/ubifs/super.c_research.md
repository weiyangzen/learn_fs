# File Research: sources/os/linux/linux-stable/fs/ubifs/super.c

## Purpose
Implements UBIFS VFS integration, mount/remount/unmount lifecycle, inode allocation/read/write/evict behavior, mount option parsing, module initialization, shrinker registration, and filesystem type registration.

## Key Behavior
- `ubifs_iget()` loads inode nodes from the TNC, validates them, initializes VFS inode operations by file type, and handles inline symlink/xattr/device data.
- Inode lifecycle hooks manage dirty inode writeback, orphan deletion, page truncation on eviction, fscrypt state, and budget release.
- `init_constants_early()`, `init_constants_sb()`, and `init_constants_master()` derive UBIFS runtime geometry, node ranges, watermarks, budgeting constants, journal limits, and statfs reporting values.
- Mount option parsing supports unmount mode compatibility flags, bulk read, data CRC checking, compressor override, assert action, and authentication parameters.
- `mount_ubifs()` is the central mount sequence: basic UBI checks, sysfs/debug init, empty-volume detection, buffer allocation, authentication init, superblock/master read, LPT init, free-space fixup, recovery, journal replay, orphan handling, GC LEB reservation, and global mount registration.
- R/W mounts mark the master dirty early; clean unmount and remount-R/O clear dirty/orphan flags and write the master node.
- `ubifs_remount_rw()` completes deferred recovery, allocates R/W-only resources, starts the background thread, reinitializes LPT writable state, and handles GC/log readiness.
- `ubifs_remount_ro()` stops the background thread, syncs write buffers, writes a clean master node, frees R/W-only buffers, and switches LPT to R/O state.
- `open_ubi()` parses device-path and nodev mount syntaxes such as `ubiX_Y`, `ubiY`, `ubiX:NAME`, and `ubi:NAME`.
- Module init creates inode slab, registers shrinker, initializes compressors/debugfs/sysfs, and registers the `ubifs` filesystem.

## Important Dependencies
- Calls into nearly every UBIFS subsystem: superblock, master, LPT, log, journal replay, recovery, orphan, GC, TNC, budgeting, authentication, debugfs, sysfs, compressors, and fscrypt.
- Uses VFS `fs_context`, `super_operations`, inode slab cache, shrinker API, and UBI volume open/close APIs.
- Uses global shrinker structures from `shrinker.c` and sysfs helpers from `sysfs.c`.

## Invariants and Risks
- `umount_mutex` is the mount/unmount/remount exclusion point and also protects against shrinker races.
- R/O and R/W mount modes allocate different resources; remount paths must mirror allocation and cleanup precisely.
- Recovery ordering is security-sensitive under authentication: size recovery is split around authenticated GC commit.
- `ubifs_fill_super()` transfers ownership of authentication option strings from fs context to `ubifs_info`.
- Mount failure paths are staged and must unwind only resources initialized up to the failure point.
