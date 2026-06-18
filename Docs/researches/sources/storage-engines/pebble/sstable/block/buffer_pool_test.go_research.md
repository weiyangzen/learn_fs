## sources/storage-engines/pebble/sstable/block/buffer_pool_test.go

Purpose: Datadriven tests for `BufferPool` allocation, release, and reuse behavior.

Important APIs/types/functions: `writeBufferPool` renders each capacity slot as `[size]` for idle, `<size>` for in-use, and `[    ]` for unused capacity. `TestBufferPool` handles `init`, `alloc`, and `release` commands against a map of named `Buf` handles.

Control flow: Each datadriven command mutates a single `BufferPool`. `init` drains any previous state, initializes with a requested capacity, and prints state. `alloc` scans or grows through `BufferPool.Alloc` and stores the returned handle. `release` releases a named handle and deletes it. A deferred drain releases active handles and the pool at test end.

State and persistence behavior: Test state persists across commands inside a datadriven file, modeling realistic pool reuse. It does not touch durable SSTable data.

Dependencies and integration points: Uses `github.com/cockroachdb/datadriven`, standard `bytes`, `fmt`, `io`, `testing`, and `BufferPool` itself.

Risks: The renderer only exposes raw allocation sizes and in-use state; it does not validate memory contents, invariant mangling, or concurrency misuse. It assumes named handle discipline in testdata.

Test signals: Good signal for slot lifecycle and pool growth/replacement behavior. It complements block reader tests that use pools indirectly.
