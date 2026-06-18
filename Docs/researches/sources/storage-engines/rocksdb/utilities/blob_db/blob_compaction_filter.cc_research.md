# sources/storage-engines/rocksdb/utilities/blob_db/blob_compaction_filter.cc

## Purpose
This file implements BlobDB's internal compaction filters. The filters remove expired or evicted blob indexes from the base DB, optionally apply the user's compaction filter to values stored in blob files, and, when garbage collection is enabled, relocate live blobs from old blob files into newly created blob files during compaction.

## Important APIs and Functions
`BlobIndexCompactionFilterBase::~BlobIndexCompactionFilterBase()` closes and registers any open output blob file, then records expired and evicted blob-index counters. `FilterV2()` is the central base-DB compaction path. Non-blob values are either kept or passed to the user compaction filter. Blob-index values are decoded with `BlobIndex::DecodeFrom()`, removed if TTL has expired, removed if their file number predates `next_file_number` and is absent from `current_blob_files`, or read from the old blob file before passing the actual blob value to the user's filter.

`HandleValueChange()` rewrites a user-modified value into a new blob file and replaces the base DB value with a new encoded blob index, returning `kChangeBlobIndex`. `OpenNewBlobFileIfNeeded()`, `ReadBlobFromOldFile()`, `WriteBlobToNewFile()`, `CloseAndRegisterNewBlobFileIfNeeded()`, and `CloseAndRegisterNewBlobFile()` encapsulate BlobDBImpl interaction for blob file creation, raw blob reads, blob log writes, output size tracking, close, and registration.

`BlobIndexCompactionFilterGC::~BlobIndexCompactionFilterGC()` logs one-pass GC stats and records GC tickers. `PrepareBlobOutput()` implements the integrated GC relocation path for compaction: decode the existing blob index, count it, keep TTL blobs and new-enough files, otherwise read the old blob, write it to a new file, encode the replacement blob index, and return `BlobDecision::kChangeValue`. `BlobIndexCompactionFilterFactory` and `BlobIndexCompactionFilterFactoryGC` build filter instances after reading current time and compaction context from `BlobDBImpl`.

## Control Flow
Base filtering starts by branching on `ValueType`. A value of `kBlobIndex` takes the internal BlobDB path; anything else is delegated to the user filter if present. For blob indexes, decode failure is conservative and keeps the value in the normal filter path. TTL expiration removes the index regardless of snapshots because the base class reports `IgnoreSnapshots() = true`. Eviction removal uses a compaction context snapshot of live blob files. If a non-TTL blob needs user filtering, the code parses the internal key to get the user key and sequence context, reads the raw blob from its file, runs the user's `FilterV2()` as a normal `kValue`, and, if changed, writes the modified value back out as a blob.

GC relocation follows a stricter path. Decode failure sets an error and returns `kCorruption`. TTL blobs are kept because this pass focuses on non-TTL stale-file cleanup. Blob files newer than or equal to `cutoff_file_number` are kept. Older blobs are copied into an output blob file, possibly rolling to a new one when `blob_file_size` is reached, and the base DB entry is updated to point at the new blob location.

## State and Persistence Behavior
The filter holds mutable `blob_file_` and `writer_` because RocksDB invokes the filter through logically const methods. New blob files remain unregistered until closed under `BlobDBImpl::mutex_`; this delays visibility until the file is immutable. `WriteBlobToNewFile()` updates the `BlobFile` record count/size and increments `BlobDBImpl::total_blob_size_`. Destructors are important persistence boundaries: any open output blob file is closed and registered even if the file never reached the target size.

The base filter accumulates expired/evicted counts and sizes, while the GC subclass accumulates all/relocated blob counts, relocated bytes, new-file count, and error state in `BlobDBGarbageCollectionStats`.

## Dependencies and Integration Points
The implementation depends on `BlobDBImpl` internals (`CreateBlobFileAndWriter`, `GetRawBlobFromFile`, `CloseBlobFile`, `RegisterBlobFile`, options, mutex, total size), `BlobFile`, `BlobLogWriter`, `BlobLogRecord`, `BlobIndex`, `ParsedInternalKey`, RocksDB compaction filter APIs, statistics tickers, `SystemClock`, logging, and `SyncPoint` test hooks.

## Risks and Edge Cases
Decode behavior differs by path: regular filtering keeps undecodable blob indexes, while GC reports corruption. User filter integration requires parsing an internal key; parse failure asserts and keeps the value. The comments note that compaction-filter instances are not called from multiple threads, so mutable counters are non-atomic. Output blob files can become numerous because each compaction can create its own files, though bounded by compaction count and configured blob size. Error handling is largely boolean and mapped to compaction decisions, so logging and ticker stats are important for diagnosis.

## Test Signals
Direct test hooks include `TEST_SYNC_POINT("BlobIndexCompactionFilterBase::WriteBlobToNewFile")`. Expected signals include blob DB ticker counters for expired/evicted indexes and GC relocation/new-file/failure counts, info/error logs during open/read/write/close failures, and compaction output decisions (`kRemove`, `kKeep`, `kChangeBlobIndex`, `kIOError`, `kChangeValue`, `kCorruption`).
