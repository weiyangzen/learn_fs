# sources/storage-engines/rocksdb/env/fs_remap.h

## Purpose
Declares `RemapFileSystem`, an abstract `FileSystemWrapper` that maps logical paths to paths in an underlying filesystem. Subclasses implement `EncodePath`, and optionally `EncodePathWithNewBasename`, to define the mapping policy.

## Important APIs and Types
- `RemapFileSystem(const std::shared_ptr<FileSystem>& base)` wraps a base filesystem.
- Pure virtual `EncodePath(const std::string& path)` returns `{IOStatus, mapped_path}`.
- Virtual `EncodePathWithNewBasename` supports operations where the leaf path may not exist yet.
- Overrides cover DB path registration, file creation/open, directory operations, existence/listing/attributes, deletion, size/time/is-directory, rename/link, sync, lock, logger, and absolute path.
- `IsInstanceOf` recognizes `RemapFileSystem` in addition to wrapper/base identities.

## Control Flow
The header defines the contract: before any operation reaches the target filesystem, logical paths must be encoded. For create-like operations, subclasses can permit a new basename while still validating the parent. For existing-object operations, encoding failure prevents delegation.

## State and Persistence
No remap state is declared in the base class. Subclasses carry any mapping state. Persistent effects are delegated to the wrapped filesystem after path translation.

## Dependencies and Integration Points
Depends on `rocksdb/file_system.h`. It integrates with RocksDB's filesystem abstraction as a reusable base for path-virtualizing filesystems. It also affects DB path registration, file locks, logger paths, and directory fsync metadata.

## Risks and Edge Cases
- The class is explicitly not a proven security boundary.
- Listing APIs expose a contract ambiguity: the base declares overrides but does not require decoded child names.
- Subclasses must preserve path normalization and parent validation; otherwise `EncodePathWithNewBasename` can become an escape vector.

## Test Signals
No direct tests are listed. Subclass tests should use a fake mapping filesystem and assert every override passes exactly the expected mapped paths to a fake target, especially create-vs-existing operations.
