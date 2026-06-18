## sources/storage-engines/pebble/sstable/block/buffer_pool.go

Purpose: Provides memory buffers for blocks either from the block cache allocation machinery or from a short-lived, non-thread-safe `BufferPool` used by compactions, metadata reads, external iteration, blob rewrites, and level checking.

Important APIs/types/functions: `Alloc` returns a `Value` backed by either `BufferPool` or `cache.Value`. `Value` exposes `BlockData`, `BlockMetadata`, `MakeHandle`, `Truncate`, `Release`, and a testing cache-install hook. `BufferHandle` abstracts cache-backed and pool-backed handles. `BufferPool.Init`, `Reason`, `Alloc`, and `Release` manage reusable `AllocedBuffer`s. `Buf.Valid` and `Buf.Release` manage pool slots. `ReasonForBufferPool` enumerates use cases.

Control flow: Pool allocation scans existing slots for an unused buffer large enough. If the pool is at capacity and has an unused too-small slot, it replaces that slot's allocation; otherwise it appends a new allocation. Releasing a `Buf` mangles bytes under invariants and nils the slot's slice to mark it reusable. `BufferPool.Release` refuses to release while any slot is still in use.

State and persistence behavior: There is no persistent format. Pool state holds `cache.Value` allocations and active subslices. The pool never shrinks during its lifetime, so peak working set affects retained memory until `Release`.

Dependencies and integration points: Used by `block.Reader.doRead` and `Alloc` to avoid populating the block cache for background or special reads. Depends on Pebble `cache`, `base`, `invariants`, and block `MetadataSize`. Cache hit/miss categories in `Reader.Read` depend on `ReasonForBufferPool`.

Risks: Not thread-safe; copying and releasing `Buf` values incorrectly may double-release or reuse live memory. `BufferHandle.Release` calls both possible backing releases; this relies on nil-safe cache release behavior and zero-value `Buf.Release`. Long-lived pools or unexpectedly large temporary blocks can retain substantial memory.

Test signals: `buffer_pool_test.go` datadriven tests exercise init, allocation, release, reuse, replacement of too-small idle buffers, and visual slot states.
