# File Research: sources/virtualization/virtiofsd/src/passthrough/device_state/serialization.rs

This file converts prepared `PassthroughFs` runtime state into serde/postcard serializable structs defined in `serialized.rs`.

Main responsibilities:
- `TryFrom<serialized::PassthroughFs> for Vec<u8>` serializes the structured state with `postcard::to_stdvec()`.
- `From<&PassthroughFs> for serialized::PassthroughFsV2` builds the full migration payload.
- `From<&PassthroughFs> for serialized::NegotiatedOpts` captures options negotiated during FUSE `INIT`.
- `InodeData::as_serialized()` converts one inode, requiring migration info.
- `InodeMigrationInfo::as_serialized()` maps preserialization locations to wire locations.
- `From<(Handle, &HandleData)> for serialized::Handle` serializes open file handles.

Inode serialization:
- Iterates every inode in `fs.inodes`.
- If an inode cannot be serialized, logs a warning and emits a `serialized::Inode` with `InodeLocation::Invalid`, preserving inode ID and refcount.
- Requires `migration_info`; missing info becomes "Failed to reconstruct inode location".
- Asserts that only `fuse::ROOT_ID` uses `RootNode` migration info.
- If `migration_verify_handles` is enabled, requires a prepared file handle and stores it for destination-side verification.

Handle serialization:
- Serializes handle ID, inode ID, and `HandleMigrationInfo`.
- Currently the only handle source is `OpenInode { flags }`.
- Invalid handles from prior failed migration are still serialized so a later destination can retry opening them.

Mount path handling:
- `MountPathsBuilder` is active only for `MigrationMode::FileHandles`.
- It maps source mount IDs, found in serialized file handles, to paths relative to the shared directory.
- If a mount root is outside the shared directory, it serializes `"."` so the destination can use the shared root.
- Mount path collection failures are warning-only; missing mount paths mean affected file-handle inodes cannot migrate.

Interactions:
- Depends on preserialization modules for `InodeMigrationInfo` and `HandleMigrationInfo`.
- Depends on `MountFds` for mount roots and `relative_path()` for shared-directory-relative paths.
- Produces `serialized::PassthroughFs::V2`, which `device_state/mod.rs` writes to the migration state pipe.

Edge cases and risks:
- This layer intentionally avoids new I/O for verification handles; missing prepared handles are internal errors.
- `mount_paths` is best effort; failure does not abort serialization but can make file-handle migration incomplete.
- Path locations require UTF-8 because the wire format stores filenames as `String`.
