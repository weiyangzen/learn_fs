# File Research: sources/virtualization/libblockdev/src/plugins/fs/generic.c

Implements generic filesystem plugin operations: supported-filesystem metadata, probing, wiping, dispatch to filesystem-specific modules, capability queries, mkfs option routing, mount-assisted operations, and freeze/thaw.

Key entry points:
- `bd_fs_supported_filesystems()` returns the filesystem names supported by this plugin.
- `bd_fs_wipe()` and `bd_fs_clean()` remove signatures with libblkid.
- `bd_fs_get_fstype()` probes the first filesystem signature using libblkid.
- `bd_fs_resize()`, `bd_fs_repair()`, `bd_fs_check()`, `bd_fs_set_label()`, and `bd_fs_set_uuid()` dispatch by explicit or detected filesystem type.
- `bd_fs_get_size()`, `bd_fs_get_free_space()`, and `bd_fs_get_min_size()` dispatch to filesystem-specific info/min-size APIs.
- `bd_fs_can_*()` functions report tool availability and feature support.
- `bd_fs_mkfs()` builds filesystem-specific mkfs extra args from `BDFSMkfsOptions`.
- `bd_fs_features()` returns static feature metadata.
- `bd_fs_freeze()` and `bd_fs_unfreeze()` issue `FIFREEZE` / `FITHAW` ioctls on mountpoints.

Core mechanics:
- Static `fs_features[]` records resize modes, mkfs option support, fsck support, configure support, ownership/partition-table semantics, partition IDs/GUIDs, and min/max size for each known filesystem.
- Static `fs_info[]` maps filesystem names to required utility names for mkfs, check, repair, resize, label, query, UUID, and min-size operations.
- `fstype_to_tech()` maps strings like `ext4`, `xfs`, `vfat`, `ntfs`, `f2fs`, `nilfs2`, `btrfs`, `udf`, and `exfat` into plugin tech IDs.
- `device_operation()` centralizes operation dispatch and reports unsupported operations with operation-specific wording.
- `fs_mount()` mounts devices to temporary directories when an operation requires a mounted filesystem, preserving existing mounts when already mounted.
- XFS quota flags are queried through `xfs_db` and translated into mount options when temporary-mounting XFS.
- XFS, NILFS2, and Btrfs have special mount-assisted resize/info/label paths.
- `query_fs_operation()` powers capability queries by checking static support and whether the required executable exists.

Important invariants:
- Generic mkfs is handled separately from `device_operation()`.
- Generic size/free/min-size functions return 0 on error and set `GError`.
- XFS resize input is converted from bytes to filesystem blocks before `xfs_growfs`.
- F2FS resize input is converted from bytes to filesystem sectors and shrink forces safe mode.
- Btrfs info and some operations require temporary mounting.
- Freeze/thaw first validates that the path is a mountpoint.

Filesystem/block relevance:
- This is the central policy and dispatch layer for the filesystem plugin. It links block-device probing, signature wiping, filesystem-specific tools, capability reporting, and mount-aware operations.

Notable risks:
- Static capability data can drift from filesystem-tool behavior.
- Several query paths depend on text output parsers in filesystem-specific modules.
- Temporary mount/unmount failures after successful operations can turn an otherwise successful operation into a reported failure.
- `bd_fs_get_fstype()` rejects non-filesystem signatures even when libblkid detects other useful block metadata.
