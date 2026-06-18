# sources/sync-backup/restic/internal/fs/node.go

Purpose: Converts filesystem metadata into `data.Node` values and restores nodes/metadata to disk.

Important APIs: `nodeFromFileInfo`, `buildBasicNode`, `nodeTypeFromFileInfo`, `nodeFillExtendedStat`, username/group lookup caches, `NodeCreateAt`, and `NodeRestoreMetadata`.

Control flow and state: Backup conversion builds a basic node, fills extended stat, generic attributes, and xattrs. Restore creation dispatches by node type to mkdir, file creation, symlink, device, FIFO, or socket no-op. Metadata restore applies ownership, xattrs, generic attributes, timestamps, and finally chmod for non-symlinks.

Dependencies and integration: Central bridge between `ExtendedFileInfo`/OS metadata and restic repository `data.Node`. Platform-specific files supply `lchown`, `utimesNano`, `mknod`, generic attributes, and xattrs.

Risks: Restore order matters, especially on Windows read-only files where chmod/file attributes can block later metadata updates. User/group name lookup caches map missing names to zero/empty values. Non-root Unix permission errors may be ignored by public `NodeRestoreMetadata`.

Test signals: `node_test.go`, `node_unix_test.go`, `node_windows_test.go`, and xattr tests validate conversion, restore, ownership, timestamps, xattrs, and error behavior.
