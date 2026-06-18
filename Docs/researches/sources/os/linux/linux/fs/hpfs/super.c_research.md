# File Research: sources/os/linux/linux/fs/hpfs/super.c

HPFS superblock, mount, remount, statfs, ioctl, and module lifecycle implementation. It wires the OS/2 HPFS filesystem into the VFS through `file_system_type`, `fs_context_operations`, and `super_operations`.

Key behavior:
- Maintains HPFS dirty/chkdsk state with `mark_dirty()` and `unmark_dirty()` by updating the spare block at sector 17.
- Centralizes filesystem error policy in `hpfs_error()`: continue, remount read-only, or panic depending on `errors=` mount option.
- Provides cycle detection helper `hpfs_stop_cycles()` for corrupt on-disk graph structures.
- Implements `hpfs_statfs()` by lazily counting free sectors from bitmap bands and free dnodes from the dnode bitmap.
- Handles HPFS-specific `FITRIM` via `hpfs_ioctl()`, gated by `CAP_SYS_ADMIN`.
- Allocates HPFS inode private objects from `hpfs_inode_cache`.

Mount interface:
- Parses `uid`, `gid`, `umask`, `case`, `check`, `errors`, `eas`, `chkdsk`, and `timeshift`.
- `hpfs_fill_super()` validates boot/super/spare blocks, loads bitmap directory and codepage table, initializes `hpfs_sb_info`, creates the root inode, and reconstructs root timestamps from the root dirent.
- Remount forbids changing `timeshift`, syncs first, updates policy fields, and marks the filesystem dirty when becoming writable.

Dependencies include HPFS helpers from `hpfs_fn.h`, block buffer mapping, bitmap helpers, fs parser APIs, VFS inode/super APIs, and user-copy helpers.

Risks and invariants:
- Mount failure paths manually unwind buffer heads and `hpfs_sb_info`; edits must preserve the `bail*` ordering.
- Dirty/clean marking is part of cross-OS recovery semantics with OS/2 chkdsk.
- `sb_timeshift` is intentionally immutable across remount.
- Bitmap free-space counts are cached and depend on HPFS bitmap integrity.
