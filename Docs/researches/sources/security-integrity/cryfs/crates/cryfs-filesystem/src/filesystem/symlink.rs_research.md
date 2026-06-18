# sources/security-integrity/cryfs/crates/cryfs-filesystem/src/filesystem/symlink.rs

## Purpose
Implements `CrySymlink`, the RustFS symlink adapter for converting back to a node and reading a symlink target from a `SymlinkBlob`.

## Important APIs, types, and functions
- `CrySymlink::new` stores a borrowed blobstore guard and shared `NodeInfo`.
- `load_blob` loads the symlink blob by id.
- `blob_as_symlink_mut` validates the blob type and maps mismatches to `CorruptedFilesystem`.
- The `Symlink` trait impl provides `into_node` and `target`.

## Control flow
`target` updates parent access timestamp according to policy while it loads the symlink blob, locks it, casts it to `SymlinkBlob`, and awaits `target()`. Unparseable target data becomes a corruption error.

## State and persistence behavior
The symlink target is persisted inside the symlink blob. Atime is persisted in the parent directory entry when policy permits. `CrySymlink` itself holds only runtime guards.

## Dependencies and integration points
Uses `ConcurrentFsBlobStore`, `FsBlob`, `SymlinkBlob`, RustFS `Symlink`, `CryNode`, and `NodeInfo` timestamp helpers.

## Risks and edge cases
The adapter reloads the blob for every target read and does not cache target text. Target errors are treated as corrupted filesystem. Like the file and directory adapters, correctness depends on parent entry type matching the actual blob type.

## Test signals
Coverage should assert symlink target round trips, atime updates on target reads, conversion back into `CryNode`, and corrupted type/target error handling.
