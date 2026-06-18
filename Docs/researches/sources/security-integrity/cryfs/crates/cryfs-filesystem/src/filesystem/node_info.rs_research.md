# sources/security-integrity/cryfs/crates/cryfs-filesystem/src/filesystem/node_info.rs

## Purpose
Centralizes metadata for root and non-root nodes: blob identity, parent directory handle, name, blob type, atime policy, optional ancestor chain, attribute reads/writes, timestamp updates, truncation, and metadata flushing.

## Important APIs, types, and functions
- `NodeInfoImpl` distinguishes `IsRootDir` from `IsNotRootDir`.
- Constructors `new_rootdir` and `new_non_root_dir` set up metadata ownership.
- Accessors include `blob_id`, `parent_blob`, `node_type`, `atime_update_behavior`, and optional ancestor helpers.
- `load_blob`, `flush_if_cached`, `getattr`, `setattr`, `truncate_file`, timestamp update helpers, and `flush_metadata` perform most metadata operations.
- `dir_entry_to_node_attrs` maps fsblobstore `DirEntry` metadata to RustFS `NodeAttrs`.

## Control flow
Root getattr fabricates attrs from current uid/gid and current time. Non-root getattr loads lstat size from the child blob and entry metadata from the parent directory. `setattr` truncates first when size is provided, then updates parent entry mode/uid/gid/atime/mtime and refreshes mtime after truncation. Read/write/list operations use concurrent wrappers to update parent timestamps and run data operations in parallel.

## State and persistence behavior
Non-root metadata persists in the parent directory entry, while file length and symlink target size are read from the child blob. Truncation mutates the file blob. Timestamp helpers mutate parent directory entries. Root metadata is currently synthetic and not persisted. `flush_metadata` flushes the parent directory blob when available.

## Dependencies and integration points
Uses `ConcurrentFsBlobStore`, `ConcurrentFsBlob`, `FsBlob`, `DirBlob`, `FileBlob`, `DirEntry`, mode/uid/gid types, RustFS `NodeAttrs`, `AtimeUpdateBehavior`, tokio join, and async-drop macros. It is shared by every node, directory, file, symlink, and open-file adapter.

## Risks and edge cases
Root attrs are synthetic and may change across calls. `setattr` asserts `ctime.is_none`, so a caller passing ctime panics rather than receiving `FsError`. Truncation before parent attr mutation can leave partial effects if later metadata update fails. Parent directory casts use `expect` in places, so internal invariant violations can panic. Timestamp updates for root are no-ops.

## Test signals
Coverage should verify getattr/setattr mapping, truncate side effects and mtime updates, root behavior, atime policy adaptation, metadata flushes, missing parent entries, corrupted child blob types, and optional ancestor chain construction.
