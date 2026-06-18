# File Research: sources/virtualization/virtiofsd/src/passthrough/file_handle.rs

This file wraps Linux file-handle APIs used to identify and reopen inodes without holding an `O_PATH` fd for every inode.

Core types:
- `FileHandle`: mount ID plus `oslib::CFileHandle`.
- `OpenableFileHandle`: a `FileHandle` paired with an `Arc<MountFd>` suitable for `open_by_handle_at()`.
- `SerializableFileHandle`: serde form containing mount ID, handle type, and handle bytes.
- `FileOrHandle`: stores an inode as a `GuestFile`, an openable file handle, or an invalid migration error.

File-handle creation:
- `from_name_at_fail_hard()` calls `name_to_handle_at()` and always returns either a handle or an error.
- `from_name_at()` returns `Ok(None)` for unsupported filesystems (`EOPNOTSUPP`) or oversized handles (`EOVERFLOW`), allowing fallback to `O_PATH` FDs.
- `from_fd_fail_hard()` and `from_fd()` use `AT_EMPTY_PATH` to address an already-open fd.

Opening:
- `FileHandle::to_openable()` asks `MountFds` for a mount FD matching the handle's mount ID.
- `OpenableFileHandle::open()` calls `open_by_handle_at()` with caller-provided flags.
- `SerializableFileHandle::to_openable()` converts serialized bytes back to `CFileHandle` and intentionally uses the destination `MountFd`'s local mount ID, not the serialized source mount ID.

Verification helpers:
- `require_equal()` compares mount ID and handle payload.
- `require_equal_without_mount_id()` compares type and payload only; this is important during migration because source and destination mount IDs differ.
- `Display` prints mount ID, handle type, and hex bytes for diagnostics.

Interactions:
- Used by `inode_store.rs` as a store key when inodes are represented by handles.
- Used by `passthrough/mod.rs` when `inode_file_handles` or file-handle migration is enabled.
- Used by serialized migration state for inode verification and file-handle locations.

Edge cases and risks:
- File handles are filesystem-dependent; unsupported or oversized handles must be handled without breaking normal operation in `Prefer` mode.
- Opening serialized handles depends on correct source-mount-ID to destination-mount-FD translation.
- `FileOrHandle::Invalid` preserves migration errors so guest operations can fail deterministically and later migrations can forward the invalid state.
