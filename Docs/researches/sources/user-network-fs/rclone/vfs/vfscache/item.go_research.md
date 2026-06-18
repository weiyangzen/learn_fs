# sources/user-network-fs/rclone/vfs/vfscache/item.go

## Purpose
Implements `vfscache.Item`, the per-file unit of rclone's VFS cache. It owns the sparse local cache file, persisted JSON metadata, downloader coordination, dirty/writeback state, and ENOSPC reset behavior for one VFS path.

## APIs, Flow, And State
Key types are `Item`, persisted `Info`, `Items` sorted by access time, `ResetResult`, and `StoreFn`. `newItem` reconciles cache file and metadata existence, loads `Info`, and estimates size. `Open`/`open` validate remote fingerprints, create cache directories/files, reuse handle-caching grace-period handles when safe, register the item back into `Cache`, and create downloaders for remote-backed files. Reads call `preAccess`, `_ensure` missing ranges, read from `fd`, and retry on no-space errors after kicking the cleaner. Writes update ranges, size, dirty metadata, and cancel pending writebacks when a new modification arrives. `Close` either starts a grace timer for clean handles or `_actualClose`s: it drains missing dirty ranges, closes downloaders and the file descriptor, saves metadata, sets cache-file modtime, and stores immediately or queues asynchronous writeback. `Reset` is the cache cleaner's recovery path, skipping dirty, grace, pending-access, or empty items and otherwise rebuilding clean cache files.

## Dependencies And Integration
Depends on `fs`, `fserrors`, `operations.Copy`, sparse-file helpers, `ranges.Ranges`, `downloaders`, and `writeback`. It is tightly coupled to `Cache` lock ordering, downloader lock ordering, and writeback lock ordering. Persistence is the local cache data file plus `toOSPathMeta` JSON. Remote integration is via `fs.Object`, fingerprints, `fcache.NewObject`, `fremote`, and `Cache.AddVirtual`.

## Risks And Test Signals
Primary risks are lock-order deadlocks, dirty data loss during stale fingerprint handling, writeback cancellation races, grace-period reuse of stale descriptors, and ENOSPC recovery leaving waiters blocked. Tests in `item_test.go` cover existence, metadata reload, dirty/truncate/read/write behavior, large sequential/random/concurrent reads, stale/remote-gone reloads, and handle-caching reset semantics.
