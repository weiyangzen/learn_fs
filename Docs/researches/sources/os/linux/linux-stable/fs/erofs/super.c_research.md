# File Research: sources/os/linux/linux-stable/fs/erofs/super.c

This file is the EROFS superblock, mount-context, module-lifetime, and VFS super-operations hub.

Major responsibilities:
- Provides EROFS logging via `_erofs_printk()` and creates/frees the `erofs_inode` slab cache.
- Reads and validates the on-disk superblock in `erofs_read_superblock()`, including magic, block size, unsupported feature bits, superblock checksum, 48-bit layout fields, metabox fields, xattr-prefix metadata, compression configuration, and device-table metadata.
- Handles multi-device and non-block-device mounting through `erofs_scan_devices()` and `erofs_init_device()`, including block-device paths, file-backed paths, fscache cookies, DAX discovery, device-table tags, and 48-bit block counts.
- Defines default and parsed mount options: `user_xattr`, `acl`, `cache_strategy`, `dax`, `device`, `fsid`, `domain_id`, `directio`, `fsoffset`, and `inode_share`.
- Implements `fs_context` operations for parsing, tree creation, reconfiguration, and cleanup.
- Fills the VFS superblock in `erofs_fc_fill_super()`: sets read-only/noatime behavior, block size, bdi, export ops, xattr handlers, POSIX ACL flags, compressed-cache state, packed/metabox/root inodes, shrinker registration, xattr prefixes, and sysfs registration.
- Supports block-device, fscache nodev, and file-backed nodev mounts in `erofs_fc_get_tree()`.
- Implements NFS export support through file-handle encode/decode and parent lookup.
- Owns superblock shutdown via `erofs_put_super()` and `erofs_kill_sb()`, releasing sysfs, shrinker, xattr prefixes, internal inodes, device contexts, fscache state, DAX references, opened files, and mount strings.
- Registers/unregisters the filesystem and subsystem dependencies in module init/exit.

Important invariants and validations:
- EROFS is mounted read-only and noatime.
- Supported block sizes are constrained by page size; fscache mode rejects non-page block sizes.
- `fsoffset` must be block-size aligned and is rejected for fscache mode.
- File-backed mounts reject stacked filesystems and nested file-backed EROFS to avoid stack-depth recursion.
- `inode_share` requires `domain_id`, is incompatible with forced DAX, and is disabled if the on-disk ishare-xattr feature is absent.
- DAX is disabled if the backing block/device path cannot provide DAX or if the block size is unsupported.
- Unknown incompatible features reject the mount.
- Metabox self-loop and invalid ishare-prefix ids are treated as corrupted metadata.

External interfaces:
- Exports `erofs_sops`.
- Registers `erofs_fs_type`.
- Optionally registers `erofs_anon_fs_type` for ondemand/page-cache-share features.
- Calls into EROFS xattr, sysfs, shrinker, fscache, compression, metabox, and inode-lookup subsystems.
