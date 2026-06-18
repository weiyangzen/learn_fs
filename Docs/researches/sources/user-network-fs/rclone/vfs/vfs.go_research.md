<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/vfs/vfs.go -->
# sources/user-network-fs/rclone/vfs/vfs.go

## Purpose
Defines the top-level VFS abstraction, common node/handle interfaces, active VFS reuse, cache setup/shutdown, directory cache refresh, stat/open helpers, filesystem statistics, file/directory convenience operations, virtual entries, symlink APIs, and metadata-file detection.

## Important APIs, Types, and Functions
Key types are `Node`, `Nodes`, `Noder`, `OsFiler`, `Handle`, `baseHandle`, and `VFS`. Key functions/methods include `Help`, `New`, `Stats`, `activeCacheEntries`, `SetCacheMode`, `Shutdown`, `CleanUp`, `FlushDirCache`, `WaitForWriters`, `Root`, `newInode`, `Stat`, `StatParent`, `decodeOpenFlags`, `OpenFile`, `Open`, `Create`, `Rename`, `Statfs`, `Remove`, `Chtimes`, `Mkdir`, `MkdirAll`, `ReadDir`, `ReadFile`, `WriteFile`, `AddVirtual`, `Readlink`, `CreateSymlink`, `Symlink`, and `isMetadataFile`.

## Control Flow
`New` copies configuration into a non-cancelled context, initializes options, reuses an active VFS with identical options when possible, registers the new VFS globally, creates root `Dir`, starts change notification and SIGHUP handling, optionally refreshes the dir cache, and enables cache mode. `OpenFile` enforces `O_RDONLY|O_TRUNC` invalidity, stats or creates a file, then delegates to node `Open`. Path operations resolve through `Stat` and `StatParent`. `Statfs` uses backend `About` or optional size walk and caches usage for `DirCacheTime`.

## State and Persistence Behavior
Maintains active VFS registry, in-use counts, root directory cache, optional disk cache, usage cache, poll channel, cancellation functions, and inode counter. Persistent effects occur through delegated file/dir operations, cache cleanup, directory creation/removal, write file, symlink creation, and cache virtual entry insertion. `Shutdown` decrements refcount before actually removing active entries and cancelling goroutines.

## Dependencies and Integration Points
Integrates with `fs.Fs` features, `vfscache`, `vfscommon.Options`, `Dir`, `File`, rc stats, filter/config contexts, change notification, `walk.ListR`, and mount-facing `Handle` interfaces. `go:generate` ties this file to generated open tests.

## Risks and Edge Cases
Active VFS reuse depends on full option equality. `WaitForWriters` logs `vfs.cache.Dump()` on timeout even when cache could be nil if writers remain without cache. `AddVirtual` ignores its `isDir` argument and always passes `false` to `Dir.AddVirtual` in this version. SIGHUP handlers are started per VFS. `Statfs` with `UsedIsSize` can be expensive because it walks the whole remote.

## Test Signals
`vfs_test.go` covers base handle defaults, construction/reuse/shutdown, permissions option initialization, root/stat/stat-parent/open/rename/statfs/mkdir/mkdir-all, missing-size filling, and metadata extension. `vfs_case_test.go` covers case-insensitive and Unicode normalization lookups.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/vfs/vfs.go -->
