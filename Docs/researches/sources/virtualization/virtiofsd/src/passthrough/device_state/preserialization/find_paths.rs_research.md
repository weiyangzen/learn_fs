# File Research: sources/virtualization/virtiofsd/src/passthrough/device_state/preserialization/find_paths.rs

## Scope

Preserialization fallback constructor that reconstructs inode locations as parent-inode plus filename paths by walking the shared directory tree.

## APIs Covered

- `InodePath` holds a strong parent inode reference and UTF-8 filename.
- `Constructor` walks the filesystem and fills inode migration info.
- `InodePath::check_presence()` validates that a recorded path still identifies the expected inode.
- Display support renders path-like diagnostic output.

## Behavior

- Starts from the FUSE root inode if mounted.
- Uses an explicit directory stack rather than recursive calls.
- Opens directories and iterates entries with `ReadDir::new_no_seek()`.
- Ignores `.` and `..`.
- Opens entries with path-resolution policy through `PassthroughFs::open_relative_to()`.
- Matches discovered entries against the inode store using file handle or inode IDs.
- For matched inodes, records `InodeMigrationInfo::Path`.
- For unmatched directories, creates temporary inode-store entries so deeper tracked children can be represented by parent paths.
- Cancels promptly when the shared cancellation flag is set.

## Validation

`check_presence()` compares device IDs and, when possible, file handles without mount IDs; otherwise it falls back to inode ID comparison. This catches stale paths and inode replacement during migration.
