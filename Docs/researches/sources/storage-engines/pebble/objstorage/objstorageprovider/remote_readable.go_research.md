# sources/storage-engines/pebble/objstorage/objstorageprovider/remote_readable.go

Purpose: This file adapts `remote.ObjectReader` into Pebble's `objstorage.Readable` and `ReadHandle` interfaces. It adds optional shared-cache reads, corruption conversion for disappeared objects, read-before buffering for metadata/index access, dynamic readahead, and compaction-specific large reads.

Important types and functions: `NewRemoteReadable` constructs a standalone readable; provider `newRemoteReadable` additionally wires file number and cache. `remoteReadable` implements `ReadAt`, `Close`, `Size`, and `NewReadHandle`. `remoteReadHandle` implements buffered `ReadAt`, `SetupForCompaction`, `RecordCacheHit`, and pooled `Close`. Constants define 1 MiB normal remote max readahead and 8 MiB compaction readahead.

Control flow: `remoteReadable.readInternal` routes through `sharedcache.Cache.ReadAt` if available; compaction reads are marked read-only so they do not populate cache. Missing-object errors from the remote driver are marked as corruption. A read handle uses read-before only on the first read, then serves prefixes from its buffer when possible. Sequential reads use `readaheadState` to increase read size and fill the buffer, capped at EOF. Compaction handles bypass dynamic state and request the fixed 8 MiB size.

State and persistence: All buffering is per handle and reused through `sync.Pool`. The shared cache may write local cache files asynchronously, but this file itself persists no metadata.

Dependencies and integration: It depends on `remote.Storage`, `sharedcache`, `objstorage.ReadBeforeSize`, and the shared readahead state. File cache/table readers use these handles for remote SST and blob access.

Risks and test signals: Risks include memory growth from buffers, incorrect EOF capping, stale buffer reuse, and expensive compaction reads. Tests exercise data-driven read-before/readahead behavior and corruption conversion after underlying remote deletion.
