# sources/storage-engines/pebble/external_iterator.go

## Purpose
Implements `NewExternalIter`, which builds a normal Pebble `Iterator` over externally supplied SSTable files without opening a DB.

## Important APIs, Types, And Functions
`NewExternalIter` and `NewExternalIterWithContext` are the public constructors. `externalIterState` owns opened `sstable.Reader`s and a block buffer pool. `validateExternalIterOpts`, `createExternalPointIter`, `finishInitializingExternal`, and `openExternalTables` handle option validation, point/range iterator construction, and reader opening.

## Control Flow
The constructor rejects unsupported iterator options, opens every provided file as an `sstable.Reader`, allocates an `Iterator`, attaches `externalIterState`, applies bounds, and initializes point and optional range-key iteration. Point iteration creates one merging level per file, assigning synthetic sequence numbers so earlier input subarrays shadow later ones. Range keys are merged through range-key iterator configuration and interleaved with points when requested. Initialization errors close already-opened readers.

## State And Persistence Behavior
The iterator is read-only and owns only transient readers, buffer pool memory, iterator stats, and synthetic sequence transforms. It does not mutate or persist DB metadata. `Close` releases all readers and the buffer pool.

## Dependencies And Integration Points
Depends on public `Options`/`IterOptions`, `objstorage.ReadableFile`, `sstable.Reader`, merging iterators, range key interleaving, block buffer pools, and table reader options. It is useful for ingest/replication/tooling paths that need Pebble semantics over raw SSTables.

## Risks And Edge Cases
Input ordering is a contract: subarrays are reverse chronological, files within subarrays are sorted and non-overlapping for points. External iterators do not support block-property filters, table filters, guaranteed durable reads, L6 filter options, or blob references. Error cleanup during initialization is important because partially opened readers otherwise leak.

## Test Signals
Covered by datadriven external iterator tests, flaky initialization error tests, blob-reference rejection, masking/bounds cases, and scan benchmarks.
