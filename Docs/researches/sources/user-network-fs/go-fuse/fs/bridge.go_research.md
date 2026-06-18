# sources/user-network-fs/go-fuse/fs/bridge.go

Purpose: core raw FUSE bridge that translates kernel requests into optional `fs` node/file interfaces while maintaining inode and file-handle bookkeeping.

Important APIs/types/functions: `rawBridge`, `fileEntry`, `ServerCallbacks`; `NewNodeFS`; request handlers for `Lookup`, `Mkdir`, `Mknod`, `Create`, `Forget`, `GetAttr`, `SetAttr`, `Rename`, `Link`, `Symlink`, xattrs, `Open`, `Read`, locks, `Release`, `Write`, `Flush`, `Fsync`, `Fallocate`, `OpenDir`, `ReadDirPlus`, `ReadDir`, `FsyncDir`, `StatFs`, `CopyFileRange`, `Ioctl`, `Lseek`, `OnUnmount`.

Control flow/state: bridge maps kernel node IDs to `Inode`, stable attrs to deduplicated inodes, allocates file handles, tracks free handles, registers backing FDs for passthrough, applies attr/entry timeouts, and uses locks ordered with inode locks before bridge mutex. `readDirMaybeLookup` handles overflow, seek offsets, interrupted reads, and readdirplus lookup.

Dependencies/integration: depends on `fuse`, `internal.HasAccess`, and interfaces from `api.go`. Risks are concurrency, lookup-count lifecycle, stale stable attrs, file-handle release races, readdir offset correctness, and passthrough reference counts. Tests cover virtual entries, type changes, negative cache, direct I/O, dir seek, cache behavior, ioctl, forget, and loopback operations.
