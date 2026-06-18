<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/sstable/colblk/data_block.go -->
# sources/storage-engines/pebble/sstable/colblk/data_block.go

## Purpose
`data_block.go` implements Pebble's columnar point-key data block format, default user-key schema, metadata initialization, validation, suffix rewriting, and hot-path iteration. It decomposes internal keys into schema-specific key columns plus trailers, prefix-change bitmap, values, external-value flags, obsolete flags, and optional tiering metadata.

## Important APIs, Types, And Functions
`KeySchema`, `KeyWriter`, `KeySeeker`, and `KeySeekerMetadata` define the customization points for database-specific user-key decomposition and search. `DefaultKeySchema` splits keys into prefix `PrefixBytes` and suffix `RawBytes`. `DataBlockEncoder` exposes `Init`, `Reset`, `Add`, `AddWithSecondaryBlobHandle`, `Rows`, `Size`, `MaterializeLastUserKey`, and `Finish`. `OptionalColumnConfig`, `NoTieringColumns`, and `WithTieringColumns` govern tiering columns. `DataBlockRewriter.RewriteSuffixes` rewrites block suffixes. `InitDataBlockMetadata`, `InitIndexBlockMetadata`, and `InitKeyspanBlockMetadata` initialize block-cache metadata. `DataBlockDecoder`, `DataBlockValidator`, and `DataBlockIter` provide read, validation, and iteration surfaces.

## Control Flow
Writing starts with `DataBlockEncoder.Init`, which creates a schema key writer and column builders. Each `Add` writes key columns, trailer, prefix-same bit, value payload, external-value bit, obsolete bit, and optional tiering fields. `Finish` inverts `prefixSame` into a persisted `prefixChanged` bitmap, writes schema and max-key-length custom headers, encodes all columns, and returns the last internal key. Reading initializes `DataBlockDecoder` from an aligned block and then builds a `KeySeeker` either per iterator or once in `block.Metadata`. Iteration routes `SeekGE`, `SeekPrefixGE`, `SeekLT`, `First`, `Last`, `Next`, `Prev`, `NextPrefix`, and `NextWithSamePrefix` through row indexes, lazily materializing keys and values only when needed.

## State And Persistence Behavior
Persistent state includes the schema custom header, a four-byte maximum user-key length, the generic column header, and all column payloads. Values that are external are stored with a leading `block.ValuePrefix`; in-place values elide that prefix. Tiering span IDs, attributes, and secondary blob handles are present only when both tiering columns are configured. `DataBlockIter` owns transient row state, reusable key buffers, block handles, transform configuration, cached prefix-range bounds, lazy tiering column decoders, and obsolete-row cursors. `InitHandle` relies on metadata previously initialized inside the block cache and releases the previous handle before adopting a new one.

## Dependencies And Integration Points
This file integrates deeply with `internal/base`, `sstable/block`, `sstable/blockiter`, `PrefixBytes`, `RawBytes`, `Bitmap`, and `UnsafeUints`. It provides the `blockiter.Data` implementation used by SSTable iterators. `DataBlockRewriter` is used by suffix rewriting paths and expects no value-block lookups. Metadata initialization converts panics to `base.CorruptionErrorf`, giving higher layers a corruption boundary around unsafe decoding.

## Risks
The code is performance-sensitive and uses unsafe casts, manual metadata packing, manual key-buffer sizing, and copied inline decode logic. Bugs can arise if `decodeKey` and inlined copies diverge, if optional column configuration mismatches the actual block format, if a caller supplies unaligned data, or if external-value handlers are nil when external values are present. `RewriteSuffixes` explicitly drops secondary blob handles and performs row-by-row rewriting. `Finish(rows, size)` supports only `Rows()` or `Rows()-1`, and the caller must provide the exact size for the chosen row count.

## Test Signals
`data_block_test.go` provides datadriven format/iterator/rewrite coverage, validation checks, writer benchmarks, decoder-init benchmarks, and randomized semantic tests for `SeekPrefixGE` plus `NextWithSamePrefix` with transforms and obsolete hiding. `data_block_meta_test.go` verifies `*WithMeta` tiering metadata paths. `data_block_iter_bench_test.go` measures common iterator operations.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/sstable/colblk/data_block.go -->
