# sources/storage-engines/pebble/internal/batchskl/skl.go

Purpose: Implements Pebble's non-concurrent in-memory skiplist index for batch records, storing node metadata separately from raw batch key/value storage.

APIs and types: `Skiplist`, `NewSkiplist`, `Reset`, `Init`, `Add`, `NewIter`, `ErrTooManyRecords`, internal `node`, `links`, random height/probability helpers, and splice search helpers.

Control flow and state: `Init` seeds random state, allocates head/tail sentinels, and links all levels. `Add` parses a batch record at `keyOffset`, extracts key boundaries, computes an abbreviated key, finds splice positions, allocates a variable-height node in a byte slice, and links base-to-top. In-order insertions use a fast path from tail. Equal keys are inserted before existing equal keys so newer batch entries iterate first.

Persistence and dependencies: Indexes external batch storage by offsets; it does not own the actual records. Node memory is a byte slice with unsafe node views and uint32 offsets. Depends on binary varints, rand/v2, unsafe, base comparer/abbreviated keys, and CockroachDB errors.

Integration points: Used by batch indexing and batch iterators. Internal keys encode the record offset with `SeqNumBatchBit` so batch entries participate in internal-key ordering.

Risks: Non-concurrent by design. Unsafe node layout and uint32 offsets require careful allocation bounds; `ErrTooManyRecords` protects against overflow. Corrupted batch record lengths return errors. Reset may retain up to 1 MiB of node memory.

Test signals: `skl_test.go` covers pointer-free layout, empty/basic behavior, ordering, overflow, iterator seeks/bounds, and benchmarks.
