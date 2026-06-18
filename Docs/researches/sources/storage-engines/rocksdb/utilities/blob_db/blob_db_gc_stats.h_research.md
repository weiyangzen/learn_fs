# sources/storage-engines/rocksdb/utilities/blob_db/blob_db_gc_stats.h

## Purpose
This header defines `BlobDBGarbageCollectionStats`, a compact per-GC-pass accumulator used by BlobDB compaction-time garbage collection to report how much blob data was encountered, relocated, and whether the pass hit an error.

## Important APIs and Types
The class exposes read accessors `AllBlobs()`, `AllBytes()`, `RelocatedBlobs()`, `RelocatedBytes()`, `NewFiles()`, and `HasError()`. Mutators are intentionally small and monotonic: `AddBlob(size)` increments total encountered blob count and bytes, `AddRelocatedBlob(size)` increments relocated count and bytes, `AddNewFile()` increments created output files, and `SetError()` marks the pass as failed.

## Control Flow and State
Instances start at zero counts with `error_ = false`. During a GC compaction pass, the compaction filter calls `AddBlob()` after decoding each blob index, `AddNewFile()` when it opens a new output blob file, `AddRelocatedBlob()` after a successful relocation, and `SetError()` when decode/read/write/close fails. The object does not reset itself; it is intended to have one instance per filter/pass.

## Persistence and Dependencies
The class has no direct persistence behavior and depends only on `<cstdint>` plus the RocksDB namespace header. Its values become observable when `BlobIndexCompactionFilterGC` logs them and records statistics tickers in its destructor.

## Risks and Test Signals
The class is not synchronized, matching the compaction-filter assumption that one filter instance is not invoked concurrently. Its counters can reveal partial progress when `HasError()` is true, so tests should check both relocation counts and failure flag. Since all methods are inline, misuse risk is mostly semantic: callers must pass blob payload sizes consistently and call `AddRelocatedBlob()` only after successful durable write/update steps.
