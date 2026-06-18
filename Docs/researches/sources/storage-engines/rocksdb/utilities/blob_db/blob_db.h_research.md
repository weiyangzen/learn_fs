# sources/storage-engines/rocksdb/utilities/blob_db/blob_db.h

## Purpose
This header declares the public BlobDB API, a `StackableDB` wrapper that stores large values in separate blob log files while storing blob indexes in the underlying RocksDB instance. It also defines BlobDB-specific constants and options.

## Important APIs and Types
Constants include `kNoExpiration` for non-TTL blobs, `kBlobDirName` for the blob directory under the base DB, and `kBytesPerSync` for incremental OS sync behavior. `BlobDBOptions` configures `max_db_size`, `ttl_range_secs`, target `blob_file_size`, `enable_garbage_collection`, `disable_background_tasks`, and supports `Dump(Logger*)`.

`BlobDB` extends `StackableDB` and restricts support to the default column family. It declares pure virtual core operations implemented by `BlobDBImpl`: default-CF `Put`, `PutWithTTL`, `Get` returning a `PinnableSlice` and optional timestamp, `Get` returning expiration, `Write`, `NewIterator`, `CompactFiles`, and `Close`. Column-family overloads check the handle ID against `DefaultColumnFamily()` and return `NotSupported` or null for non-default handles.

The class exposes two static `Open()` overloads: one for simple `Options`, and one for `DBOptions` plus a vector of column-family descriptors/handles. `DestroyBlobDB()` is declared to destroy both base DB and BlobDB content using `BlobDBOptions`.

## Control Flow Contract
Users open BlobDB through the static factory and then use it like a RocksDB wrapper with additional TTL-aware operations. Writes place values in blob files and indexes in the base DB; reads resolve indexes back to blob values. Unsupported operations such as `SingleDelete` and `Merge` return `NotSupported` because BlobDB cannot safely express their semantics against external blob storage.

## State and Persistence Behavior
The header documents the persistence model: blobs live under `blob_dir` while the base DB stores locations. TTL range controls bucketing of blob files by expiration window, and `blob_file_size` controls when a file becomes immutable. Garbage collection, when enabled, rewrites live blobs from stale non-TTL files during compaction. `Close()` is pure virtual, signaling that implementations must explicitly flush/close both base DB and blob state.

## Dependencies and Integration Points
This is a public utility header depending on `rocksdb/db.h`, `rocksdb/status.h`, and `StackableDB`. It integrates with standard RocksDB write/read/iterator/compaction APIs while intentionally narrowing column-family and operation support.

## Risks and Test Signals
The main API risks are accidental use with non-default column families, unsupported merge/single-delete expectations, TTL expiration semantics, and the split persistence boundary between base DB and blob files. Tests should check status returns for unsupported CFs/operations, TTL reads with expiration output, iterator behavior over blob-backed values, compaction/GC side effects, and `DestroyBlobDB()` cleanup.
