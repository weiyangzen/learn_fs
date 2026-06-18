# sources/storage-engines/pebble/sstable/random_test.go

## Purpose
`random_test.go` stress-tests SSTable point iterators under random table shapes and injected read errors. Its primary contract is that if a file-read error is injected during an iterator operation, the operation must not silently return a key while hiding the error.

## Important APIs, Types, and Functions
- `TestIterator_RandomErrors` runs 50 seeded subtests.
- `runErrorInjectionTest` builds a randomized SSTable, wraps reads with `errorfs`, creates a `Reader`, constructs a point iterator, and executes 1000 random valid operations.
- `opRunner` tracks current iterator direction, last operation, current KV, and whether the last operation was `SeekPrefixGE`.
- `randomTableConfig` parameterizes writer options, keyspace, key count, value sizes, suffix/sequence ranges, and RNG.
- `buildRandomSSTable` writes sorted randomized internal keys through `NewRawWriter`.

## Control Flow
Each seed creates a memfs file, randomizes writer options across table formats, block sizes, index sizes, optional bloom filters, optional block-property collectors, column key schemas, and lowest-level behavior. After writing 10,000 random internal point keys, the test reopens the file through an `errorfs.Toggle` and `Counter`; injection begins only after `NewReader` succeeds.

The iterator is created with optional test-key block-property filters, randomized filter-block use (`AlwaysUseFilterBlock` or `NeverUseFilterBlock`), `MakeTrivialReaderProvider`, and `AssertNoBlobHandles`. A metamorphic weighted deck chooses among `SeekGE`, `SeekPrefixGE`, `SeekLT`, `First`, `Last`, `Next`, `NextPrefix`, and `Prev`. Operation runners skip invalid direction/state transitions, ensuring exactly one valid operation per loop iteration.

Before and after each operation, the test compares the injected-error counter. If an error was injected, the test asserts the iterator did not return a KV and that `it.Error()` is non-nil; otherwise it logs the latest operation and key.

## State and Persistence Behavior
The generated SSTable is persisted in memfs and read through Pebble's normal object-storage readable path. The test exercises persistent encodings across randomized table formats, index layouts, filter blocks, block property metadata, key schemas, point key kinds, sequence numbers, and values. It intentionally does not persist range deletion or range-key data.

Iterator state tracked in `opRunner` mirrors API preconditions: `Next` is only run after reverse positioning and not after `SeekPrefixGE`; `NextPrefix` requires a valid forward position; `Prev` is not run from an already reverse-exhausted state.

## Dependencies and Integration Points
- Uses `vfs.NewMem`, `objstorage.NewSimpleReadable`, and `objstorageprovider.NewFileWritable`.
- Uses `errorfs.Toggle`, `Counter`, and random injector to simulate read failures in the storage layer.
- Uses `testkeys` comparer/keyspace and `colblk.DefaultKeySchema` for suffix-rich keys and column-block compatibility.
- Integrates with table filters (`bloom`), block stats (`block.ReadEnv`), block property filters, and value-block reader provider setup.
- Uses `metamorphic.Weighted` for reproducible operation distributions.

## Risks and Edge Cases
- The test checks error surfacing, not equivalence with a no-error oracle; wrong successful results without injected errors may pass.
- It only tests point iterators; comments note range deletion and range-key iterators are not covered.
- Error injection probability and random operation selection make this high-value but non-exhaustive; failures require seed logs for reproduction.
- The writer randomization uses very small and very large block/index sizes, increasing coverage of single-level/two-level and boundary seek paths.

## Test Signals
This is a broad stochastic signal over read-time failure handling for the iterator state machine. It is especially relevant to lazy index/data/filter loading, `TrySeekUsingNext`, prefix seeks with bloom filters, block-property skipping, and reverse/forward direction changes. The saved stack trace on injection helps identify swallowed-error paths.
