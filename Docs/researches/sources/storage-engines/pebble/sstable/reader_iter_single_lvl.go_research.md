# sources/storage-engines/pebble/sstable/reader_iter_single_lvl.go

## Purpose
`reader_iter_single_lvl.go` implements the generic single-level SSTable point iterator for both row-oriented and column-oriented data blocks. It owns lazy top-level index loading, data block loading, bounds handling, bloom-filter prefix seeks, block-property filtering, virtual SSTable bounds, synthetic-key optimization, value-block reading, iterator pooling, and debug tree-step output.

## Important APIs, Types, and Functions
- `exhaustedBounds` distinguishes not exhausted, lower-bound exhausted, upper-bound exhausted, and prefix exhausted states.
- `singleLevelIterator[I, PI, D, PD]` stores context, comparer, bounds, block-property filters, reader, read handles, error state, read env, optimization state, filter state, transforms, prefix state, maximum-suffix synthetic-key state, embedded index/data iterators, and pool metadata.
- Constructors `newColumnBlockSingleLevelIterator` and `newRowBlockSingleLevelIterator` initialize row/column-specific data iterators and value-block readers.
- Positioning methods implement `SeekGE`, `SeekGEWithMeta`, `SeekPrefixGE`, `SeekLT`, `First`, `FirstWithMeta`, `Last`, `Next`, `NextWithMeta`, `NextPrefix`, and `Prev`.
- Helpers include `ensureIndexLoaded`, `loadDataBlock`, `resolveMaybeExcluded`, `skipForward`, `skipBackward`, `virtualLast`, `bloomFilterMayContain`, and reset/close methods.

## Control Flow
Construction calls `init`, which records options, constrains bounds for virtual SSTables, creates preallocated read handles for index/filter and data reads, records transforms and maximum suffix property, and deliberately does not read the index block. Row and column constructors perform format assertions, install value-block readers when table attributes require them, and initialize embedded block iterators.

`ensureIndexLoaded` is the lazy gate. The first positioning operation reads the top-level index block through `reader.readTopLevelIndexBlock`, initializes the embedded index iterator, records `indexLoaded`, and leaves later operations to reuse it.

`loadDataBlock` requires a loaded and valid index. It decodes the current index entry, avoids reloading the same valid data block, invalidates stale data on block changes, consults block-property filters, resolves bound-limited maybe-excluded blocks, reads the data block, initializes the embedded data iterator, and computes per-block lower/upper bounds.

Forward seeks clear prefix state for `SeekGE`, optionally clamp to virtual lower bounds, handle `TrySeekUsingNext` and monotonic bounds optimizations, seek the index on the slow path, load a block, seek within it, enforce upper bounds, and call `skipForward` when a block is exhausted or irrelevant. Reverse seeks mirror this through `SeekLT`, lower-bound checks, and `skipBackward`.

`SeekPrefixGE` sets `i.prefix`, handles synthetic-key optimization when a maximum-suffix property can safely defer the real seek, checks bloom filters when enabled, preserves loaded data blocks on clean bloom misses, and then delegates to `seekGEHelper` with prefix-aware data-block seeking. `Next` resolves a synthetic key by performing the deferred seek before normal advancement.

`First` and `Last` perform absolute positioning with special handling for configured lower/upper bounds and virtual inclusive upper bounds. `NextPrefix` advances by prefix successor, first within the current data block and then by index seek/step.

`Close` delegates to `closeInternal`, closes embedded iterators and read handles, releases block-property filterers, closes value-block readers, calls the close hook, returns the first error, resets reusable fields, and returns the iterator to its pool.

## State and Persistence Behavior
The iterator reads immutable SSTable state but maintains substantial transient positioning state. Important state includes current index/data block handles, `err`, prefix mode, exhausted-bound reason, last bloom result, loaded-index flag, per-block bounds, read handles, value-block reader, and synthetic-key buffers.

Persistent behavior depends on index separators, block handles with properties, filter blocks, table properties, value-block indexes, and virtual SSTable internal bounds. Synthetic-key optimization uses reader `UserProperties` and `MaximumSuffixProperty` to return a temporary `InternalKeyKindSyntheticKey` with `SeqNumMax`; the real seek is deferred until the synthetic key is advanced.

## Dependencies and Integration Points
- Depends on `Reader` block read wrappers and table metadata.
- Embeds `rowblk` or `colblk` index/data iterators through generic constraints from `reader_iter.go`.
- Uses `block.ReadEnv` and `objstorage.ReadHandle` for IO, stats, and readahead behavior.
- Uses `BlockPropertiesFilterer` to skip irrelevant blocks.
- Uses `tableFilterReader` through `bloomFilterMayContain`.
- Uses `valblk.MakeReader` and implements value-block reads for lazy values.
- Integrates with virtual SSTables through `virtual.VirtualReaderParams` in `ReadEnv`.
- Integrates with `treesteps` for visual debugging.

## Risks and Edge Cases
- Bounds, prefix, and data-exhaustion states are intentionally distinct; collapsing them can make `TrySeekUsingNext` incorrectly return nil or skip later prefixes.
- Bloom-filter misses preserve loaded data blocks and do not position the iterator; callers must respect the API restriction on following operations.
- Block-property filters can skip blocks without loading them; reverse iteration needs extra index stepping to determine whether maybe-excluded blocks are wholly within filter bounds.
- Virtual SSTable bounds require extra lower-bound enforcement in `skipForward` after reverse scans because skipped blocks may become relevant after filter changes.
- `resetForReuse` uses unsafe byte clearing up to `clearForResetBoundary`; field placement must be maintained carefully.
- Synthetic-key optimization is only safe when prefix containment and maximum-suffix ordering invariants hold.
- Lazy index loading shifts IO errors from construction to first use, so callers must check `Error()` after iterator operations.

## Test Signals
`reader_iter_test.go` directly covers lazy index-load errors, row/column basic iteration, seek operations, resource cleanup, concurrent independent iterators, boundary cases, stress operations, and bloom-miss non-invalidation for single- and two-level iterators. `random_test.go` adds randomized table formats and injected IO failures. `reader_iter_treesteps_test.go` checks treesteps recording for iterator operations.
