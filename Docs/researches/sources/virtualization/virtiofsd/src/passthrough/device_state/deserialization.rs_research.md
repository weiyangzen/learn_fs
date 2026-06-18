# File Research: sources/virtualization/virtiofsd/src/passthrough/device_state/deserialization.rs

## Scope

Destination-side migration restore logic for passthrough filesystem state.

## APIs Covered

- `TryFrom<Vec<u8>> for serialized::PassthroughFs` via `postcard`.
- `serialized::PassthroughFsV1::apply()` and `apply_with_mount_paths()`.
- `serialized::PassthroughFsV2::apply()`.
- `serialized::NegotiatedOpts::apply()`.
- Inode deserialization helpers for root, path, full path, invalid, and file-handle locations.
- Handle deserialization for reopened inode-backed handles.

## Behavior

- Applies source-negotiated writeback, submount, POSIX ACL, and supplementary group settings, failing if destination configuration cannot support source-enabled features.
- Clears inode store and reconstructs root first when mount-path data is needed for file-handle reopen.
- Repeatedly processes serialized inodes, deferring path entries whose parent inode is not restored yet.
- Restores root from destination config but uses source refcount and optional file-handle identity check.
- Path locations are opened relative to parent inodes with `O_PATH | O_NOFOLLOW | O_CLOEXEC`.
- File-handle locations require source mount ID resolution through V2 mount path metadata.
- Invalid or failed inodes either abort migration or are installed as guest-error placeholders based on `migration_on_error`.
- Reopens handles by opening their associated inode with sanitized preserved flags.

## Risks And Invariants

- Detects unresolved inode dependency cycles.
- Optional file-handle checks protect against path races and inode reuse.
- Destination must not enable source-disabled negotiated behavior without renegotiation; it explicitly applies source state.
