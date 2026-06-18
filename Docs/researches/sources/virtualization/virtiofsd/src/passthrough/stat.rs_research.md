# File Research: sources/virtualization/virtiofsd/src/passthrough/stat.rs

This file provides the passthrough stat wrapper used throughout the filesystem. It normalizes Linux `statx()` output into `libc::stat64` plus a mount ID.

Core types:
- `MountId = u64`.
- `StatExt`: `st: libc::stat64` and `mnt_id: MountId`.
- `SafeStatXAccess`: internal trait for accessing only valid `statx` fields based on `stx_mask`.

Main behavior:
- `SafeStatXAccess::stat64()` converts valid `STATX_BASIC_STATS` fields into a zero-initialized `libc::stat64`.
- `SafeStatXAccess::mount_id()` returns `stx_mnt_id` only when `STATX_MNT_ID` is present.
- `get_mount_id()` falls back to `name_to_handle_at()` mount ID when kernel `statx()` lacks mount ID support.
- `do_statx()` invokes `libc::syscall(libc::SYS_statx)` directly instead of relying on a libc wrapper.
- `statx()` defaults path to an empty C string, uses `AT_EMPTY_PATH | AT_SYMLINK_NOFOLLOW`, requests basic stats and mount ID, and returns `ENOSYS` if basic stats are missing.

Interactions:
- Used by lookup, getattr, file-handle validation, mount FD creation, migration path link counts, and xattr/permission helpers.
- `MountId` is a core part of inode identity in `inode_store.rs`.

Edge cases and risks:
- On kernels before `STATX_MNT_ID`, mount ID falls back to file-handle support and then to `0`.
- A mount ID of `0` weakens submount identification and file-handle diagnostics.
- Direct syscall use improves portability across libc versions but remains Linux-specific.
