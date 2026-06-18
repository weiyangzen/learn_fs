## sources/sync-backup/restic/internal/fuse/snapshots_dir.go

Purpose: FUSE directory and symlink nodes for the generated snapshot namespace.

Important APIs/types: `SnapshotsDir` stores `Root`, inode metadata, `SnapshotsDirStructure`, a prefix into the metadata tree, and a per-directory `treeCache`. `NewSnapshotsDir` constructs a pseudo directory. `Attr` returns read-only directory attrs. `ReadDirAll` refreshes snapshot metadata for the prefix, emits `.`/`..`, and converts each `MetaDirData` child to `fuse.Dirent`. `Lookup` resolves children into `snapshotLink`, snapshot root directories via `newDirFromSnapshot`, or nested `SnapshotsDir` instances. `snapshotLink` implements a read-only symlink to a generated latest target.

Control flow and state: both listing and lookup call `dirStruct.UpdatePrefix`, so repository snapshot changes are visible after `SnapshotsDirStructure` reload rules permit. Child FUSE nodes are cached by name and removed when their `Forget` callback runs.

Dependencies and integration points: depends on `SnapshotsDirStructure` for logical metadata, `inodeFromName` for stable pseudo inodes, FUSE interfaces, and `newDirFromSnapshot` in the directory implementation for actual snapshot trees. It unwraps context cancellation errors via `unwrapCtxCanceled` from `dir.go`.

Risks and test signals: the `Lookup` cache stores a node by name even though `meta` can be refreshed; stale cached nodes may persist until FUSE forgets them. Directory order is map iteration order, so callers should not rely on stable listing order. Tests cover top-level ownership, stable node objects, block count for latest links, and directory-structure generation.
