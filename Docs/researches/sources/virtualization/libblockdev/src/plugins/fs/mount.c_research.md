# File Research: sources/virtualization/libblockdev/src/plugins/fs/mount.c

Implements libblockdev mount/unmount helpers and mount table queries using libmount.

Key entry points:
- `bd_fs_mount()` mounts a device or fstab-specified entry.
- `bd_fs_unmount()` unmounts a device or mountpoint, with optional lazy/force flags.
- `bd_fs_get_mountpoint()` returns one mountpoint for a mounted device.
- `bd_fs_is_mountpoint()` checks whether a path is a mountpoint.

Core mechanics:
- `MountArgs` carries device, mountpoint, fstype, options, unmount spec, lazy, and force values.
- `do_mount()` builds a libmount context, sets source/target/fstype/options, performs the mount, then translates libmount/syscall/helper errors.
- `do_unmount()` builds a libmount context, enables lazy/force if requested, performs unmount, and translates errors.
- Separate old/new libmount error paths are compiled depending on `LIBMOUNT_NEW_ERR_API`.
- On old libmount, read-only fallback is implemented manually for some `EROFS`/`EACCES` cases.
- `run_as_user()` forks and runs mount/unmount in a child after changing real UID/GID, returning serialized error text through a pipe.
- `bd_fs_mount()` and `bd_fs_unmount()` parse supported extra args: `run_as_uid` and `run_as_gid`.

Important invariants:
- Mount requires at least a device or a mountpoint.
- UID/GID delegation requires the process to be effectively root.
- Unsupported extra args are rejected.
- Mount/unmount error codes are normalized to `BD_FS_ERROR` values, including auth and unknown filesystem cases.
- Mountpoint lookup uses parsed mtab with a libmount cache.

Filesystem/block relevance:
- This file is the filesystem plugin’s bridge to kernel mounts, needed directly by user APIs and indirectly by generic operations that require online filesystems.

Notable risks:
- Error behavior differs by libmount API version.
- Error propagation through child exit status is limited by `BD_FS_ERROR` code ranges and pipe serialization.
- `bd_fs_get_mountpoint()` returns only one mountpoint when a source is mounted multiple times.
