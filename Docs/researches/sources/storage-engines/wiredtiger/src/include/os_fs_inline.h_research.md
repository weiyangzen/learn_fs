# sources/storage-engines/wiredtiger/src/include/os_fs_inline.h

## Purpose
Provides inline wrappers around `WT_FILE_SYSTEM` directory and file-name operations, adding WiredTiger path resolution, readonly assertions, verbose tracing, diagnostic open-handle checks, durable flags, and cleanup of allocated paths.

## Important APIs, Types, And Functions
- `__wt_fs_file_system` returns the active filesystem, honoring session bucket storage.
- `__wt_fs_directory_list` and `__wt_fs_directory_list_single` resolve directory paths and call filesystem list methods.
- `__wt_fs_directory_list_free` releases list memory through the filesystem.
- `__wt_fs_exist` resolves and tests file existence.
- `__wt_fs_remove` removes a file with optional durability and diagnostic open-handle validation.
- `__wt_fs_rename` resolves both paths and renames durably if requested.
- `__wt_fs_size` resolves a path and returns file size.

## Control Flow
Wrappers initialize output pointers, build full paths with `__wt_filename`, call the active `WT_FILE_SYSTEM` vtable with `(WT_SESSION *)session`, and free temporary path strings. Remove and rename assert not readonly and, in diagnostic builds, reject operations on open handles.

## State And Persistence Behavior
Directory listings and existence/size checks are read-only filesystem observations. Remove and rename mutate persistent filesystem state, optionally with `WT_FS_DURABLE`. Temporary path buffers are allocated and freed per call.

## Dependencies And Integration Points
Depends on session filesystem selection (`S2FS`/bucket storage), path construction, filesystem extension vtables, diagnostic handle lookup, readonly flags, durable flags, and memory management. Used by metadata, backup, checkpoint, salvage, import, and file lifecycle code.

## Risks
Every path allocation must be freed on all error paths. Diagnostic open-handle checks are intentionally layering-violating but catch unsafe file lifecycle operations. Filesystem extensions must implement list-free pairing correctly. Bucket-storage sessions can route to alternate filesystems.

## Test Signals
Tests should cover default and bucket filesystem selection, list/list-free pairing, path allocation cleanup on errors, readonly remove/rename assertions, durable flag propagation, open-handle diagnostic failures, and filesystem extension error propagation.
