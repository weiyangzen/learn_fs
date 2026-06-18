# sources/user-network-fs/rclone/cmd/serve/nfs/cache.go

## Purpose

`cache.go` implements NFS file-handle cache selection, path rewriting for subpath mounts, disk-backed handle storage, metadata handle suffixing, and stale-handle handling.

## Important APIs, Types, and Functions

`Cache` defines `ToHandle`, `FromHandle`, `InvalidateHandle`, and `HandleLimit`. `Handler.getCache` selects memory, disk, or symlink cache. `pathRewriter` normalizes subpath mount handles to root-VFS absolute paths. `diskHandler` stores hash-to-path mappings and handles metadata suffixes. Helpers include `newDiskHandler`, `hashPath`, `handleToPath`, `isMetadataFile`, `isMetadataHandle`, and disk read/write/remove/suffix methods.

## Control Flow

Disk handles are MD5 hashes of cleaned full paths, stored under a sharded cache directory. Metadata files use the underlying file handle plus a four-byte suffix. `FromHandle` removes and validates suffixes, reads the mapped path, appends metadata extension if needed, and returns the root billy filesystem plus split path. Invalid or missing mappings become NFS stale handle errors.

## State and Persistence Behavior

Memory cache state is process-only. Disk and symlink caches persist mappings under the configured cache dir. Mutexes protect disk cache operations.

## Dependencies and Integration Points

It integrates go-nfs handle APIs, rclone VFS metadata extension, rclone cache dir/config string, OS path encoding, and Linux symlink cache extension.

## Risks and Test Signals

Risks include MD5 path collisions, stale cache entries after rename/delete failures, metadata suffix length constraints required by Linux NFS clients, cache-dir permissions, and subpath handle consistency. `cache_test.go` covers CRUD, stale handles, concurrency for disk/symlink caches, metadata handles, and subpath handle stability.
