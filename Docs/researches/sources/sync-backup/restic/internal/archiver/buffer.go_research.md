# sources/sync-backup/restic/internal/archiver/buffer.go

Purpose: Provides a small reusable buffer pool used by the archiver file saver when chunking file contents. It reduces allocations for normal chunk buffers while avoiding retention of unexpectedly large slices.

Important APIs and types: `buffer` holds `Data []byte` and a back-pointer to its `bufferPool`. `buffer.Release` returns the buffer to the pool only when it came from a pool and its capacity does not exceed the pool default. `bufferPool` wraps `sync.Pool`; `newBufferPool(defaultSize int)` initializes the pool; `Get` retrieves a `*buffer`.

Control flow and state: `sync.Pool.New` creates buffers with `Data` sized to `defaultSize`. Callers may mutate or reslice `Data`. On release, oversized buffers are discarded by not putting them back, preventing a single large chunk/read from permanently raising memory pressure.

Dependencies and integration: The only dependency is `sync`. The main integration point is `fileSaver.saveFile`, which obtains buffers for `chunker.Next` and releases them from async upload callbacks.

Risks and test signals: Correctness depends on every buffer user calling `Release`, including error paths and async callbacks. Reusing buffers before upload callbacks finish would corrupt data, so release timing is critical. `buffer_test.go` verifies reuse and large-buffer discard behavior despite `sync.Pool` GC nondeterminism.
