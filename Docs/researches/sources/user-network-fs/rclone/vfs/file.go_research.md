<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/vfs/file.go -->
# sources/user-network-fs/rclone/vfs/file.go

## Purpose
Defines `File`, the VFS node for regular files and symlink payload files. It bridges directory-cache nodes, backend `fs.Object`s, open handles, writeback cache entries, rename/remove operations, stat metadata, symlink resolution, and modtime/size reporting.

## Important APIs, Types, and Functions
Key members are `File`, `newFile`, `Mode`, `Path`, `CachePath`, `ModTime`, `Size`, `SetModTime`, `Open`, `Truncate`, `Remove`, `rename`, `resolveNode`, `setObject`, `waitForValidObject`, `addWriter`, `delWriter`, and the internal `o_SYMLINK` flag. `File` satisfies the package `Node` interface and returns itself through `Node()`.

## Control Flow
Creation stores parent `Dir`, path, leaf, inode, context, object, and initial size, then detects symlink status from the link suffix. `Open` resolves symlinks unless `o_SYMLINK` is set, rejects `O_RDONLY|O_TRUNC`, derives read/write intent from flags, and chooses `ReadFileHandle`, `WriteFileHandle`, or `RWFileHandle` based on cache mode, append/truncate/create flags, and whether the cache already has the item. Rename updates the VFS node immediately, then either moves the backend object and cache entry immediately or defers the remote rename until writers close. `Truncate` first forwards to open writer handles; if none remain it opens/truncates through the normal handle path.

## State and Persistence Behavior
State is guarded by `mu`, `muRW`, atomics, and lock-ordering comments that make `File` subordinate to `Dir`. Persistent effects include remote object moves/removes, cache renames/removes, delayed writeback via open handles, cached dirty item size/modtime, pending modtime application after object creation, and delayed rename callbacks. `virtualModTime` preserves stable modtimes for remotes without modtime support. Symlinks are represented by backend objects with `fs.LinkSuffix` in cache/remote paths when `--links` is enabled.

## Dependencies and Integration Points
Depends on `fs.Object`, `operations.Move`, `vfscommon.CacheMode`, `vfscache.Cache`, `Dir` methods, VFS options, and handle constructors in `read.go`, `write.go`, and `read_write.go`. `resolveNode` integrates with `VFS.Stat` and handle reading. Mount layers consume `Node`/`Handle` behavior through this file.

## Risks and Edge Cases
Deadlock risk is explicit; methods must not call most `Dir` APIs with `File.mu` held. `setSymlink` and `renameDir` use `RLock` while mutating fields, which is unusual and worth reviewing. `ModTime` writes `virtualModTime` in a deferred closure after releasing the initial read lock, so race safety depends on broader usage. Delayed rename chains can report only through logs if they fail. `waitForValidObject` waits up to roughly five seconds for writers and returns `ENOENT` on timeout. Symlink resolution only follows direct file symlinks, not symlinked intermediate directories, and is capped by `MaxSymlinkIterations`.

## Test Signals
`file_test.go`, `read_write_test.go`, and `vfs_test.go` cover basic metadata, read/write open selection, unknown-size reads, remove/remove-all, pending modtimes, cache-mode rename behavior, writer-delayed rename, size updates, and open flag matrices. Symlink behavior is not strongly represented in this subset.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/vfs/file.go -->
