<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/objstorage/noop_readahead.go -->
## sources/storage-engines/pebble/objstorage/noop_readahead.go

Purpose: provides a trivial `ReadHandle` implementation for `Readable` implementations that do not support readahead or sequential-read optimization.

Important APIs and types: `NoopReadHandle` stores a `Readable`. `MakeNoopReadHandle` constructs it. Methods implement `ReadHandle`: `ReadAt`, `Close`, `SetupForCompaction`, and `RecordCacheHit`.

Control flow: `ReadAt` delegates directly to the underlying `Readable.ReadAt`. `Close`, `SetupForCompaction`, and `RecordCacheHit` are no-ops.

State and persistence: only holds a reference to the wrapped readable. It performs no buffering and persists nothing.

Dependencies and integration: used by `SimpleReadable.NewReadHandle` in `objstorage.go` and any simple object readers that cannot benefit from readahead.

Risks and edge cases: because `Close` is a no-op, lifetime remains governed by the underlying `Readable`. Implementations returning the same no-op handle must still respect concurrency expectations of `ReadHandle` callers.

Test signals: no direct tests in the listed set; behavior is indirectly covered through object readers using `SimpleReadable`.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/objstorage/noop_readahead.go -->
