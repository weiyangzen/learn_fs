# sources/sync-backup/restic/internal/archiver/buffer_test.go

Purpose: Unit tests for the archiver buffer pool.

Important APIs and functions: `TestBufferPoolReuse` obtains a buffer, records its backing slice address, releases it, and checks that a later `Get` can reuse the same slice. `TestBufferPoolLargeBuffers` grows a buffer past the default capacity and checks that a subsequent buffer does not keep that larger capacity.

Control flow and state: Both tests retry up to 100 times because `sync.Pool` may drop entries during garbage collection. The large-buffer test mutates `buf.Data` with `append`, so it covers the exact retention risk handled by `Release`.

Dependencies and integration: Uses Go's `testing` package only and targets `newBufferPool`, `Get`, and `Release` in `buffer.go`.

Risks and test signals: The tests are deliberately tolerant of `sync.Pool` nondeterminism. They signal memory-retention regressions and broken reuse, but do not assert strict pool capacity or lifetime guarantees.
