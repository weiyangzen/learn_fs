# File Research: sources/virtualization/libblockdev/src/plugins/fs/mount.h

Declares the libblockdev mount helper API.

Key contents:
- `bd_fs_unmount()` for lazy/force unmounts with optional extra args.
- `bd_fs_mount()` for mounting by device and/or mountpoint with optional fstype/options/extra args.
- `bd_fs_get_mountpoint()` for source-to-target lookup.
- `bd_fs_is_mountpoint()` for mountpoint validation.

Filesystem/block relevance:
- Exposes mount operations and mount table queries to the generic filesystem plugin.

Notable risks:
- The compact API does not expose all libmount options directly; extensibility is via validated `BDExtraArg` keys.
