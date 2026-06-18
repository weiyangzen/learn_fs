## `sources/storage-engines/rocksdb/utilities/blob_db/blob_db_iterator.h`

Purpose: defines `BlobDBIterator`, an `Iterator` wrapper that exposes user values from a base DB iterator whose values may be blob indexes. It is the iterator read-side bridge from LSM entries to blob-file payloads.

Important APIs and functions: constructor takes an optional owned `ManagedSnapshot`, an `ArenaWrappedDBIter`, the owning `BlobDBImpl`, `SystemClock`, and statistics. Standard iterator methods delegate positioning to the base iterator and then call `UpdateBlobValue()`. `value()` returns `iter_->value()` for inline values or the cached `PinnableSlice value_` for blob entries. `status()` combines base iterator status with blob value fetch status.

Control flow: `SeekToFirst`, `SeekToLast`, `Seek`, `SeekForPrev`, `Next`, and `Prev` all record statistics, move the base iterator, and loop while `UpdateBlobValue()` returns true. `UpdateBlobValue()` resets cached value/status, checks `iter_->IsBlob()`, and calls `blob_db_->GetBlobValue(iter_->key(), iter_->value(), &value_)`. If the blob lookup returns `NotFound`, usually due to TTL expiry or missing file, it tells the caller to advance again; other non-OK status stops iteration and is surfaced.

State and persistence behavior: the iterator owns or borrows a snapshot supplied by `BlobDBImpl::NewIterator()`, ensuring blob files remain protected consistently with the base iterator sequence. It does not mutate persistent state. It stores only the current blob payload and error status.

Dependencies and integration: depends on `ArenaWrappedDBIter`, `ManagedSnapshot`, BlobDB implementation internals, `StopWatch`, statistics tickers, and `PinnableSlice`. It is constructed by `BlobDBImpl::NewIterator()` with `expose_blob_index=true` so it can see and decode blob index entries.

Risks: iterator refresh is unsupported. Expired/missing blob values are silently skipped as `NotFound`, which matches TTL semantics but can hide file disappearance as an absent key during iteration. Any blob read corruption becomes iterator status and invalidates `Valid()`. The class holds raw pointers to `BlobDBImpl`, clock, and statistics; lifetime is safe only while the DB remains open.

Test signals: `BlobDBTest::VerifyDB()` validates forward iteration against expected maps across many tests. TTL tests indirectly verify expired entries are skipped rather than returned.
