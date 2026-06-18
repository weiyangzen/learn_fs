# sources/storage-engines/rocksdb/env/fs_remap.cc

## Purpose
Implements the path-remapping filesystem wrapper declared in `fs_remap.h`. It translates user-visible paths through subclass-provided `EncodePath` or `EncodePathWithNewBasename`, then delegates the operation to `FileSystemWrapper`. It is a base for views such as chroot-like, encrypted-name, or otherwise transformed filesystems.

## Important APIs and Functions
- `EncodePathWithNewBasename` defaults to `EncodePath`.
- `RegisterDbPaths` and `UnregisterDbPaths` encode path vectors before forwarding.
- All file open/create/delete/query methods encode relevant paths and forward to the wrapped filesystem.
- `NewDirectory` wraps returned `FSDirectory` in a local `RemapFSDirectory` so `DirFsyncOptions::renamed_new_name` is encoded before directory fsync.
- `RenameFile` and `LinkFile` encode both source and destination with correct existing/new-basename semantics.

## Control Flow
Each method computes an encoded path pair, returns the non-OK status immediately if encoding fails, then delegates. Existing paths generally use `EncodePath`; paths that may not yet exist use `EncodePathWithNewBasename`. `RenameFile` converts a source `NotFound` from encoding into `PathNotFound` before returning. `NewDirectory` encodes the directory path, opens the wrapped directory, and then interposes only the fsync-with-options path mapping.

## State and Persistence
This class stores no additional state beyond the wrapped filesystem. Persistent effects are those of the delegated operations after path translation: file creation, rename, link, delete, sync, lock, and logger creation.

## Dependencies and Integration Points
Depends on `env/fs_remap.h` and `rocksdb/file_system.h`. It is designed for subclasses that define the actual path mapping policy. Integration points include DB path registration, file creation/open paths, directory fsync metadata, and file locking.

## Risks and Edge Cases
- `ReuseWritableFile` appears to compute both the new encoded path and old encoded path, but forwards `status_and_old_enc_path.second` as both arguments. That means the requested new name is ignored and reuse/rename behavior is likely wrong for remapped filesystems.
- `GetChildren` and `GetChildrenFileAttributes` return wrapped filesystem names without decoding them back to logical names; subclasses or callers must tolerate encoded child names, or this base class is incomplete for list operations.
- The class comment warns it has not been fully analyzed for strong security guarantees.
- Any subclass that allows partial mappings must carefully distinguish `EncodePath` and `EncodePathWithNewBasename` to avoid creating outside the intended view.

## Test Signals
No local tests are listed. High-priority tests should cover `ReuseWritableFile` path arguments, directory fsync rename-name mapping, list output expectations, rename `NotFound` to `PathNotFound`, and register/unregister mapping.
