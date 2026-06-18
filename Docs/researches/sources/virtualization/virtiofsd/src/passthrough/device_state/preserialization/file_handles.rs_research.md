# File Research: sources/virtualization/virtiofsd/src/passthrough/device_state/preserialization/file_handles.rs

## Scope

Preserialization constructor for migration mode that represents inodes by Linux file handles.

## APIs Covered

- `FileHandle` wrapper around `SerializableFileHandle`.
- `Constructor` for collecting file handles for all tracked inodes.
- Conversion from `FileHandle` to shared `InodeLocation`.
- Display implementation for diagnostics.

## Behavior

- Iterates the inode store unless cancellation is requested.
- Skips inodes that already have up-to-date migration info.
- For file-backed inodes, generates a file handle from the FD.
- For handle-backed inodes, reuses the existing handle.
- Invalid inodes report their prior migration error.
- Stores `InodeMigrationInfo` with optional verification handle depending on config.

## Design Notes

The pass is best-effort: failures are logged per inode, and missing migration info can later serialize as invalid, letting the destination decide based on `migration_on_error`.

## Invariants

File-handle locations contain no strong inode references, so their reference-walk helper is a no-op.
