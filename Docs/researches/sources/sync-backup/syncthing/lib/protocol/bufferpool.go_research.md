## sources/sync-backup/syncthing/lib/protocol/bufferpool.go

Purpose: global bucketed byte-slice pool for protocol buffers sized around valid block sizes.

Important APIs: global `BufferPool`, `bufferPool`, `newBufferPool`, `Get`, `Put`, `getBucketForLen`, and `putBucketForCap`.

Control flow and state: `newBufferPool` creates one `sync.Pool` per block size plus a small-message bucket. `Get` chooses the smallest bucket satisfying the requested length, returns a slice with requested length and bucket capacity, or allocates exact size for oversized requests. `Put` requires slices with capacities matching known buckets and panics for invalid capacities or non-empty lengths depending on implementation checks. Bucket selection is tied to `BlockSizes` initialized in `bep_fileinfo.go`.

Dependencies and integration points: used by protocol message read/write paths to reduce allocations. Must be initialized after block sizes.

Risks: callers must only put slices obtained from the pool and with expected length/capacity state. Invalid put usage can panic. Holding pooled buffers after put can corrupt data.

Test signals: `bufferpool_test.go` covers bucket selection, invalid put panics, and concurrent stress.
