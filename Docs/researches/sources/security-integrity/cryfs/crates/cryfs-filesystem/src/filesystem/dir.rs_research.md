# sources/security-integrity/cryfs/crates/cryfs-filesystem/src/filesystem/dir.rs

## Purpose
Implements `CryDir`, the directory adapter used by RustFS to look up, list, create, remove, rename, move, and fsync CryFS directory entries stored in `DirBlob`s.

## Important APIs, types, and functions
- `CryDir::new` binds a shared blobstore guard to shared `NodeInfo`.
- Helpers create flushed child blobs (`create_dir_blob`, `create_file_blob`, `create_symlink_blob`) before adding parent entries.
- `lookup_child`, `rename_child`, `move_child_to`, `entries`, `create_child_dir`, `remove_child_dir`, `create_child_symlink`, `remove_child_file_or_symlink`, `create_and_open_file`, and `fsync` implement the `Dir` trait.
- `blob_as_dir`/`blob_as_dir_mut` convert entry-type expectations into `CorruptedFilesystem` errors.

## Control flow
Lookup loads the directory blob, reads a matching entry under lock, then constructs child `NodeInfo` that keeps the parent blob alive. Creation loads the parent and creates the child blob concurrently; if parent insertion fails, it removes the just-created blob. Removal first validates type and emptiness when needed, removes the parent entry, flushes the parent to avoid dangling entries, then removes the child blob. `move_child_to` loads source and destination parents, optionally checks ancestor cycles, removes the old entry, adds or overwrites the new entry, updates the moved blob's parent pointer, then updates source/destination parent mtimes.

## State and persistence behavior
Directory entries carry names, blob ids, entry type, mode, uid/gid, atime, mtime, and ctime. This code intentionally orders persistence: newly created blobs are flushed immediately before parent references are created, and removed parent entries are flushed before deleting the target blob. Directory data fsync flushes the directory blob; full fsync also flushes parent metadata.

## Dependencies and integration points
Depends on `ConcurrentFsBlobStore`, `DirBlob`, `FsBlob`, fsblobstore entry errors, `cryfs_rustfs::object_based_api::Dir`, path components, async-drop utilities, and `check_entry_overwrite_allowed` from `device.rs`. It creates `CryNode`, `CryOpenFile`, and `CrySymlink` adapters for child results.

## Risks and edge cases
Several operations release and reacquire locks, and comments call out race conditions in removal and move paths. Move has incomplete rollback if destination insertion or parent-pointer update fails after source removal. Create paths map some insertion failures to `UnknownError` after cleanup. `create_and_open_file` currently ignores open flags, and symlink attrs compute size from the link name rather than the target.

## Test signals
No in-file tests. Expected integration tests should assert POSIX-like directory behavior: duplicate create, lookup miss, rmdir non-empty, unlink-vs-rmdir type errors, flush ordering on failures, rename overwrite rules, cross-directory moves, timestamp updates, and optional ancestor cycle rejection.
