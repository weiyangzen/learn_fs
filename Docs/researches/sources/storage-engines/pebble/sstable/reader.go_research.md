# sources/storage-engines/pebble/sstable/reader.go

## Purpose
`reader.go` implements the SSTable `Reader`, the object that owns file-level metadata, block handles, table attributes, comparer/schema selection, and block-reading entry points. It constructs point and range iterators, reads metadata/properties/layout information, validates block checksums, estimates disk usage, and provides value-block access for lazy values.

## Important APIs, Types, and Functions
- `Reader` stores `block.Reader`, table format, block handles for index/meta/filter/range/value/properties/blob/tiering blocks, comparer, key schema, attributes, user properties, table filter, and cached error state.
- `ReadEnv` carries virtual SSTable parameters, shared-ingestion mode, block read environment/stats, and internal bounds used by synthetic-key optimization.
- `IterOptions` configures point iterator bounds, transforms, block property filters, filter-block size policy, read env, value/blob readers, and maximum-suffix property.
- `NewReader` opens and validates the file footer, metaindex, properties, table attributes, comparer, merger, and key schema.
- `NewPointIter`, `NewIter`, and `NewCompactionIter` choose single-level vs two-level and row vs column iterators.
- `NewRawRangeDelIter` and `NewRawRangeKeyIter` read range-keyspan blocks and apply virtual truncation/foreign-SST transformation when needed.
- `ReadPropertiesBlock`, `Layout`, `ValidateBlockChecksums`, `EstimateDiskUsage`, and `CollectBlockEntries` expose metadata and block-usage functionality.
- `MakeTrivialReaderProvider` adapts a long-lived reader into `valblk.ReaderProvider`.

## Control Flow
`NewReader` verifies the input readable, applies default options, uses a preallocated read handle, reads the footer, initializes `blockReader`, and records top-level handles. It reads the metaindex and properties with metadata buffer pools to avoid polluting the block cache. It derives `Attributes` from properties and verifies footer attributes for Pebble v7+. It then resolves the comparer, merger, and column key schema, recording errors on the reader and returning failure when metadata is inconsistent or unknown.

`newPointIter` dispatches by `AttributeTwoLevelIndex` and `tableFormat.BlockColumnar()` to construct the matching row/column single- or two-level iterator. `newCompactionIter` disables filter-block use, applies shared-ingested obsolete-point hiding, constructs the same iterator family, and calls `SetupForCompaction` to alter read-handle behavior.

Block reading methods are thin wrappers around `blockReader.Read` with the correct `blockkind` and optional metadata initialization functions. Metadata initialization is needed for columnar index/data/keyspan blocks.

`readAndDecodeMetaindex` reads the metaindex block, validates its decoded size, and decodes either the older row format or Pebble v6+ columnar metaindex. `initMetaindexBlocks` extracts known meta block handles, rejects obsolete v1 range-deletion blocks, and binds the first matching filter decoder to `tableFilter`.

`Layout` walks the top-level index and, when needed, second-level index blocks, building a `Layout` with all data, index, filter, range, value, properties, metaindex, blob, and tiering block handles. `ValidateBlockChecksums` sorts all present blocks by offset and reads them sequentially to verify checksums. `EstimateDiskUsage` and `CollectBlockEntries` walk index entries without reading data blocks, scaling estimates for value-block overhead using properties.

## State and Persistence Behavior
`Reader` persists no new data itself; it interprets the immutable SSTable file. It eagerly reads file metadata required to safely operate and lazily reads most data/index/filter/value blocks through iterator paths. `Close` closes the underlying `blockReader`, preserves the first error, and then marks the reader with `errReaderClosed` so later operations fail.

Persistent compatibility hinges on footer format, metaindex block names, properties fields, filter-family names, range deletion/key block names, value-block index handles, and column key schema names. `UserProperties` from the properties block are exposed on the reader and later used by iterator synthetic-key optimization.

## Dependencies and Integration Points
- Depends on `objstorage` and `block.Reader` for storage IO and caching.
- Integrates with `rowblk`/`colblk` for index/data/keyspan decoding.
- Integrates with `keyspan` and `rangekey` for range deletion/key iteration and virtual shared-SST transformations.
- Integrates with `valblk` for external value blocks and lazy values.
- Uses `virtual.VirtualReaderParams` to constrain bounds for virtual SSTables.
- Uses `ReaderOptions` comparers, mergers, filter decoders, key schemas, cache/file numbers, and init read stats.

## Risks and Edge Cases
- Unknown comparer, merger, or column key schema makes the reader unusable; unknown column key schema currently panics after setting `r.err`.
- Metadata buffer pools must be released correctly to avoid retaining large blocks.
- Two-level index layout and disk-usage estimation rely on correct index separator semantics and block-handle decoding.
- Virtual SSTables require careful bounds constraining for point and range-key iterators, especially shared-ingested range key sequence transformation.
- `ReadPropertiesBlock` intentionally bypasses the block cache; callers expecting cache warm-up will not get it.
- `NewReader` leaves the readable open on error; callers retain cleanup responsibility as documented.

## Test Signals
The adjacent tests exercise reader creation from fixtures and memfs SSTables, lazy iterator error paths, random read-error injection, bloom-filter behavior, concurrent iterator creation, resource cleanup, boundary tables, and treesteps integration. Broader repository tests likely cover layout/checksum/disk-usage APIs.
