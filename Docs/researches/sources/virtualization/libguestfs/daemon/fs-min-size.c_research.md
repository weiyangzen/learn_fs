# File Research: sources/virtualization/libguestfs/daemon/fs-min-size.c

Implements filesystem minimum-size dispatch for shrink planning.

Important behavior:
- `do_vfs_minimum_size` calls `do_vfs_type` and dispatches by filesystem type.
- ext filesystems use `ext_minimum_size(device)`.
- NTFS uses `ntfs_minimum_size(device)`.
- btrfs and xfs require a current mountpoint, found through `do_mountpoints`, then call mountpoint-based helpers.
- Unsupported types return `NOT_SUPPORTED`.

Filesystem relevance: abstracts minimum shrink size across filesystem implementations and highlights which filesystems require mounted state for size probing.
