# sources/storage-engines/rocksdb/utilities/blob_db/blob_compaction_filter.h

## Purpose
This header declares the BlobDB compaction-filter stack used to interpret blob-index values during RocksDB compaction. It provides non-GC and GC variants plus factories that wrap any user-defined compaction filter while preserving BlobDB's internal cleanup rules.

## Important APIs and Types
`BlobCompactionContext` is the per-compaction snapshot provided by `BlobDBImpl`; it carries the owning implementation pointer, `next_file_number`, and the set of currently live blob files. `BlobCompactionContextGC` carries a `cutoff_file_number` used by garbage collection to decide which non-TTL blobs are old enough to relocate.

`BlobIndexCompactionFilterBase` derives from `LayeredCompactionFilterBase`. It overrides `IgnoreSnapshots()` to return true, `FilterV2()` to handle `kBlobIndex` entries, and `IsStackedBlobDbInternalCompactionFilter()` to identify itself as BlobDB's internal stacked filter. Protected helpers open output blob files, read old blobs, write relocated/changed blobs, and close/register output files. It stores BlobDB context, the compaction-time clock value, optional statistics, mutable output file/writer handles, and counters for expired/evicted blob indexes.

`BlobIndexCompactionFilter` is the non-GC concrete filter. `BlobIndexCompactionFilterGC` adds `BlobCompactionContextGC`, a mutable `BlobDBGarbageCollectionStats`, a destructor that reports GC stats, an override of `PrepareBlobOutput()`, and an output-file open override that counts created files.

`BlobIndexCompactionFilterFactoryBase` stores `BlobDBImpl`, `SystemClock`, `Statistics`, direct user compaction filter, and user compaction filter factory from `ColumnFamilyOptions`. `BlobIndexCompactionFilterFactory` and `BlobIndexCompactionFilterFactoryGC` create the corresponding filter types.

## Control Flow Contract
The factories are called by RocksDB during compaction setup. They obtain current time from `SystemClock`, ask `BlobDBImpl` for compaction context, optionally construct a per-compaction user filter from the user's factory, and return a BlobDB internal filter that layers user behavior under BlobDB's expiration/eviction/relocation rules.

## State and Persistence Behavior
The header makes clear that compaction filters manage persistent blob-file side effects in addition to returning filter decisions. Output file and writer members are mutable because compaction callback methods are const. The comment on counters states the instance is factory-created and not called from multiple threads, so counter updates are intentionally not atomic.

## Dependencies and Integration Points
The declarations depend on internal blob index encoding, `BlobDBImpl`, `BlobDBGarbageCollectionStats`, `LayeredCompactionFilterBase`, RocksDB compaction filter interfaces, statistics, and `SystemClock`. The API is not a public BlobDB user surface; it is a bridge between BlobDB's internal file lifecycle and RocksDB's compaction machinery.

## Risks and Test Signals
The main risks are lifetime and ownership of user filters, const-but-mutating file handles, non-atomic counters, and ensuring user compaction filters see real blob values while RocksDB persists blob indexes. Test and runtime signals come from concrete `Name()` strings, statistics tickers in the implementation, and the filter's special `IsStackedBlobDbInternalCompactionFilter()` marker.
