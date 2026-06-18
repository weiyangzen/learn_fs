## sources/storage-engines/pebble/sstable/block_property.go

Purpose: Implements Pebble's block-property collection and filtering infrastructure: concise per-block/table properties used to skip data/index blocks and whole SSTables during iteration.

Important APIs/types/functions: `BlockPropertyCollector`, `BlockPropertyFilter`, `BoundLimitedBlockPropertyFilter`, `BlockIntervalCollector`, `IntervalMapper`, `BlockInterval`, `DecodeBlockInterval`, `BlockIntervalSuffixReplacer`, `BlockIntervalFilter`, `shortID`, `blockPropertiesEncoder`, `blockPropertiesDecoder`, `BlockPropertiesFilterer`, `IntersectsTable`, and internal `intersects`/`intersectsFilter`.

Control flow: Writers call `AddPointKey` for point entries, `AddRangeKeys` for range spans, `FinishDataBlock`, `AddPrevDataBlockToIndexBlock`, `FinishIndexBlock`, and `FinishTable`. `BlockIntervalCollector` unions point intervals into data/index/table state and range-key intervals directly into table state. Encoded block properties omit empty properties and store non-empty values as shortID byte, uvarint length, payload. Readers initialize a `BlockPropertiesFilterer` by testing table-level user properties and mapping property names to file-local short IDs; later per-block filtering decodes properties up to relevant short IDs, returning `blockIntersects`, `blockExcluded`, or `blockMaybeExcluded` for bound-limited filters.

State and persistence behavior: Table user properties store property name to string whose first byte is the file-local short ID and whose remainder is the table-level property. Block/index entries store compact shortID/property streams. `BlockInterval` encodes non-empty `[Lower,Upper)` as two uvarints: lower and width. Empty intervals encode as nil. The short ID limit is 256 collectors per SSTable.

Dependencies and integration points: Used by SSTable writers, index entries, reader/iterator block skipping, synthetic suffix handling, and range-key masking. Depends on `base.BlockPropertyFilter`, `base.CorruptionErrorf`, `SyntheticSuffix` from the SSTable/blockiter alias context, unsafe string-to-byte conversion, `sync.Pool`, and invariants.

Risks: Semantics are intentionally nondeterministic with respect to block boundaries and can surface extra KVs; value-dependent properties are unsafe with value separation. Bound-limited filtering is subtle and requires iterator-side proof that block bounds are within filter bounds. Encoded property corruption can break iteration. Unsafe conversion assumes filters do not mutate property bytes. Synthetic suffix support requires collectors/filters to implement replacement correctly.

Test signals: `block_property_test.go` extensively covers interval encode/decode, unions/intersections, collector sequencing, encoder/decoder sparse properties, table initialization, per-block filtering, full writer/reader datadriven cases, bound-limited masking, and suffix replacement helpers.
