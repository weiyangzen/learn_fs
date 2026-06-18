<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/vfs/vfscache/cache.go -->
# sources/user-network-fs/rclone/vfs/vfscache/cache.go

## Purpose
Implements the VFS disk cache manager: local data/meta roots, cache item registry, writeback queue access, cache reload, rename/remove, virtual entry callback, quota/age cleanup, out-of-space handling, stats, and background cleaner.

## Important APIs, Types, and Functions
Key type is `Cache`; key APIs are `New`, `Stats`, `Queue`, `QueueSetExpiry`, `Item`, `Exists`, `InUse`, `DirtyItem`, `Rename`, `DirRename`, `Remove`, `SetModTime`, `CleanUp`, `KickCleaner`, `TotalInUse`, `Dump`, and `AddVirtual`. Important internals include path conversion helpers, `reload`, `purgeOld`, `purgeClean`, `purgeOverQuota`, `purgeEmptyDirs`, `updateUsed`, quota checks, and `cleaner`.

## Control Flow
`New` computes encoded cache paths under the rclone cache dir, creates data and metadata roots, creates local backend handles, selects a common hash, initializes maps and writeback queue, reloads existing cache files/meta, purges empty dirs, and starts a cleaner goroutine. Item access normalizes names and lazily creates `Item`s. Cleaner runs immediately and on interval or kick, purging by age, quota, and clean reset eligibility, then updates systemd status.

## State and Persistence Behavior
Persistent cache state lives under `vfs` and `vfsMeta` roots. In-memory state tracks `item`, `errItems`, `used`, `outOfSpace`, cleaner kick status, and writeback queue. Rename moves data/meta files and remaps item keys. Remove deletes item state and local files and reports whether upload was pending. Cleanup removes both root trees.

## Dependencies and Integration Points
Depends on `vfscache.Item` and `writeback`, local backend via `fs/cache`, disk usage checks, `operations.Rmdirs`, `systemd.UpdateStatus`, `vfscommon.Options`, path encoding, and VFS `AddVirtual` callback. `VFS.SetCacheMode`, `RWFileHandle`, and rc queue/stats endpoints use this cache.

## Risks and Edge Cases
Cache and item lock ordering is critical. `KickCleaner` blocks callers until `outOfSpace` clears. `purgeClean` can leave dirty or in-use data and tracks failed resets in `errItems`. `reload` logs per-item reload failures but continues. Path encoding around Windows UNC and drive separators is delicate. Quota behavior relies on local disk usage availability and may treat unsupported disk usage as OK.

## Test Signals
`cache_test.go` covers creation, open counts, mkdir/purge, age purge, quota purge, min-free-space checks, clean reset purge, in-use/dirty/existence/remove/rename, cleaner loop, modtime, total in use, dump, stats, queue, and queue expiry plumbing.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/vfs/vfscache/cache.go -->
