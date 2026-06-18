# File Research: sources/virtualization/virtiofsd/src/passthrough/mount_fd.rs

This file manages open mount file descriptors used with `open_by_handle_at()` and file-handle migration.

Core types:
- `MountFd`: one open FD on a mount, its local mount ID, and a weak pointer back to the mount-FD map.
- `MountFds`: shared map from mount ID to weak `MountFd`, plus `/proc/self/mountinfo`, optional prefix stripping, and per-mount error suppression.
- `MPRError`: mount-point-related error with optional mount ID/root context and a `silent` flag.

Mount FD creation:
- `MountFd::new()` opens a path relative to a directory with `O_RDONLY`, stats it to get the local mount ID, and optionally inserts or reuses an entry in `MountFds`.
- `MountFds::get()` first tries to upgrade an existing weak entry.
- If missing, it finds the mount root from mountinfo, opens it with `O_PATH`, verifies the mount ID with `statx()`, ensures the mount point is regular file or directory, reopens it read-only, and stores it.

Mount root lookup:
- `get_mount_root()` rewinds and reads `/proc/self/mountinfo`.
- It searches for the requested mount ID and extracts the mount path column.
- If `mountprefix` is set, it strips that prefix, returning `/` for the shared root mount or mounts outside the prefix.

Error handling:
- `MPRError::Display` adds filesystem mount ID and/or mount root context when known.
- `error_for_nolookup()` marks repeated mount-ID errors as silent.
- `error_for()` augments non-silent errors with mount root lookup where safe.

Lifecycle:
- `MountFd::drop()` removes its weak map entry only when the entry's strong count is zero, avoiding races with concurrent replacement.
- The weak-map design means the cache does not keep mount FDs alive without active users.

Interactions:
- `file_handle.rs` uses `MountFds::get()` to make file handles openable.
- `serialization.rs` uses `get_mount_root()` to serialize source mount IDs to shared-directory-relative paths.
- `passthrough/mod.rs` creates `MountFds` when file handles or file-handle migration are enabled.

Edge cases and risks:
- Mountinfo parsing is intentionally simple and column-oriented; unusual escaped mount paths are worth auditing if path fidelity matters.
- Mount points that are not regular files or directories are rejected because they cannot be safely reopened read-only.
- Mount IDs are local to a host, so serialized file handles must be translated through paths on migration.
