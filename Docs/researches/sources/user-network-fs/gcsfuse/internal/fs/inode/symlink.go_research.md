# sources/user-network-fs/gcsfuse/internal/fs/inode/symlink.go

Purpose: implements symlink inode support backed by GCS objects. It supports legacy gcsfuse symlinks where the target is stored in custom metadata, and newer standard symlinks where metadata marks the object as a symlink and the object content stores the target path.

Important APIs/types: `SymlinkMetadataKey` is the legacy metadata key, while `StandardSymlinkMetadataKey` is the reserved standard key. `IsSymlink` recognizes any legacy key presence and only recognizes the standard key when its value is `"true"`. `SymlinkInode` implements `Inode` with immutable id, `Name`, `SyncerBucket`, source `Generation`, attributes, target, and metadata, plus mutex-protected lookup count. `NewSymlinkInode` initializes inode attributes from `gcs.MinObject`, records source generation/size/metageneration, initializes lookup count, and resolves the target before returning.

Control flow and state: `resolveSymlinkTarget` prioritizes standard symlinks by opening a generation-pinned reader and reading the object body; legacy symlinks return metadata directly. `openReader` calls `SyncerBucket.NewReaderWithReadHandle` with the object name and source generation. Not-found on that exact generation is wrapped as `gcsfuse_errors.FileClobberedError`, preserving stale-handle semantics. `Source` reconstructs a `gcs.MinObject` from inode state, and `UpdateSize` only mutates generation size metadata, not the target string.

Dependencies and integration: integrates with GCS read APIs, `gcsx.SyncerBucket`, FUSE inode attributes, lookup-count lifecycle, logger warnings on close failures, and the broader inode interface used by filesystem operations such as `ReadSymlink`, lookup, and unlink.

Risks: standard symlink target resolution requires a GCS read during inode construction, so missing or clobbered objects fail creation. Metadata is retained by map reference rather than deep copy. Legacy and standard metadata conflict behavior is fixed by priority: standard `"true"` wins over legacy target. `Attributes` ignores the clobbered-check flag and returns cached attrs.

Test signals: internal and external symlink tests cover detection, attribute/source reporting, size update, legacy and standard target resolution, generation clobbering, read errors, and invalid metadata errors.
