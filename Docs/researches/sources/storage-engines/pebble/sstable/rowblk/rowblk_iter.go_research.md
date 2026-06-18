# sources/storage-engines/pebble/sstable/rowblk/rowblk_iter.go

## Purpose
Implements iterators over Pebble's row-oriented block format. `Iter` reads blocks containing internal keys, while `RawIter` reads row blocks with raw user keys. The file is in the critical read path for SSTable data, range deletion, range key, index, and properties blocks, so it contains many manual varint and binary-search fast paths.

## Important APIs, Types, And Functions
`Iter` implements `blockiter.Data` and supports `Init`, `InitHandle`, `SeekGE`, `SeekPrefixGE`, `SeekLT`, `First`, `Last`, `Next`, `NextPrefix`, `NextWithSamePrefix`, `Prev`, `KV`, `Valid`, `Close`, `Describe`, and metadata-returning variants. It tracks restart offsets, current and next entry offsets, decoded key/value state, reverse-iteration caches, synthetic prefix/suffix transforms, hidden obsolete point filtering, synthetic sequence numbers, and lazy value handling for TableFormatPebblev3 value prefixes.

`RawIter` provides the same block-walking mechanics for non-internal-key row blocks and exposes `SeekGE`, `First`, `Last`, `Next`, `Prev`, `Key`, `Value`, `All`, and `Describe`. `KVEncoding` and `DescribeKV` support diagnostic formatting. `decodeVarint` and `decodeRestart` are hot helpers used throughout the iterators.

## Control Flow And State
Initialization parses the restart count from the block suffix, computes the restart table boundary, stores an unsafe pointer to the block bytes, applies any synthetic prefix buffer initialization, and pre-decodes the first user key for lower-bound checks. Forward movement decodes `{shared, unshared, valueLen}` varints, reconstructs prefix-compressed keys into `fullKey` when necessary, points values into the block data, decodes the internal trailer, applies hidden-obsolete and synthetic-seqnum rules, optionally replaces key suffixes, and constructs either in-place or lazy value handles.

Seeking performs binary search over restart points, then linearly scans within a restart region. Reverse iteration cannot decode prefix-compressed entries backwards, so it replays from the preceding restart point and caches entries in `cached`/`cachedBuf`; switching from reverse back to forward repopulates `fullKey` before continuing. Synthetic suffix seeking has extra off-by-one handling because the restart binary search happens on original on-disk suffixes while returned keys use the replacement suffix.

`NextPrefix` has a TableFormatPebblev3-specific path that uses the value prefix's `SetHasSamePrefix` bit and the high bit in restart entries to skip many MVCC versions with the same prefix before falling back to `SeekGE`. `NextWithSamePrefix` stores a copied prefix for repeated same-prefix advancement.

## Persistence And Integration
The iterator does not persist data itself; it interprets immutable serialized block bytes produced by `rowblk.Writer` and owned either directly or through a `block.BufferHandle`. `Close` releases the handle and preserves reusable buffers. It integrates with SSTable readers through `blockiter.Data`, `base.InternalKV`, `block.GetInternalValueForPrefixAndValueHandler`, `blockiter.Transforms`, and table-format features described in `sstable/table.go`.

## Dependencies
Key dependencies are `internal/base` for internal keys and comparers, `sstable/block` for lazy values and block handles, `sstable/blockiter` for transform contracts, `treeprinter`/`treesteps` for diagnostics, `invariants` for debug checks, and unsafe pointer arithmetic for speed.

## Risks
The main risks are memory-safety and corruption sensitivity around unsafe varint reads, restart offsets, invalid blocks, and very large offsets. Synthetic suffix logic relies on strong invariants: no duplicate prefixes in a suffix-replaced block and comparator ordering of replacement suffixes versus original suffixes. Hidden obsolete points complicate seeks and reverse iteration. Lazy value prefix handling assumes SET values are non-empty when value prefixes are enabled. Because many routines are manually inlined for speed, bug fixes must be applied consistently across duplicated decode paths.

## Test Signals
`rowblk_iter_test.go` exercises raw iteration, datadriven internal iteration, key stability, reverse-to-forward direction changes, synthetic prefix and suffix transforms, and randomized `IsLowerBound` checks. `unsafe_test.go` covers the shared unsafe varint decoder. Table-level iterator benchmarks in `single_lvl_iter_benchmark_test.go` provide performance signal for construction and first-seek paths.
