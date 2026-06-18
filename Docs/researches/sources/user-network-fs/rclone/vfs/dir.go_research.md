# sources/user-network-fs/rclone/vfs/dir.go

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/vfs/dir.go -->
## sources/user-network-fs/rclone/vfs/dir.go

Purpose: implements the VFS directory node: directory metadata, directory listing cache, virtual entries for pending changes, cache invalidation, lookup, creation, deletion, rename, metadata pseudo-files, and recursive operations.

Important APIs and control flow: `newDir` creates a `Dir` with inode, modtime, items map, and cleanup timer. Node methods expose type, mode, name/path, sys data, inode, modtime, size, fs/vfs, and sync/truncate behavior. Cache operations include `ForgetAll`, `ForgetPath`, `changeNotify`, `invalidateDir`, `_readDir`, `_readDirFromEntries`, and `readDirTree`. Virtual state (`vAddFile`, `vAddDir`, `vDel`) is managed by `AddVirtual`, `DelVirtual`, `_purgeVirtual`, and `manageVirtuals` so pending uploads/deletes survive remote listing lag. File-system operations include `Stat`, `ReadDirAll`, `Open`, `Create`, `Mkdir`, `Remove`, `RemoveAll`, `RemoveName`, and `Rename`.

State, dependencies, and integration: `Dir` holds VFS pointer, backend fs, parent, path, `fs.Directory` entry, read timestamp, cached `items`, virtual-state map, user sys value, modtime, cleanup timer, and atomic count of virtuals in this subtree. It integrates with `File`, `VFS`, `vfscache`, backend `fs.Fs`, `list`, `walk`, `operations`, unicode normalization, and metadata APIs.

Risks and test signals: concurrency is managed with several locks and recursive locking, so lock ordering matters. Virtual entries deliberately prevent cache eviction while uploads/writes are in progress. `statMetadata` assumes base node entry behavior and creates memory objects for JSON metadata. Rename updates cached paths and cache backing store, and must keep parent item keys in sync. Tests cover methods, cache forgets, walking, stat/listing, virtual entries, create/mkdir/remove/rename, open-file virtual survival, modtime invalidation, metadata pseudo-files, and read-only errors.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/vfs/dir.go -->
