# sources/storage-engines/pebble/sstable/copier.go

## Purpose
Implements `CopySpan`, an approximate block-level SSTable subset copier. It copies whole intersecting data blocks to a new SSTable without decompressing/re-encoding every key.

## Important APIs, Types, and Functions
- `CopySpan` is the main entry point.
- `ErrEmptySpan` reports when no blocks can include the requested span.
- `indexEntry` stores an index separator and block handle with properties.
- `intersectingIndexEntries` finds data-block index entries intersecting `[start, end)`, including two-level indexes.
- `copyWholeFileBecauseOfUnsupportedFeature` falls back to byte-for-byte whole-file copy when unsupported attributes are present.

## Control Flow
`CopySpan` closes input on exit, falls back for unsupported features, configures a raw writer without filters/block property collectors, reads metaindex/properties/filter/index, copies original properties, finds intersecting blocks, and writes blocks either from cache or grouped reads through the writer. Finally it closes the writer and returns the output metadata size.

## State and Persistence Behavior
The output SSTable contains whole original data blocks for the approximate span, an updated index and footer, a copied filter, and copied table properties that may overcount. It omits block properties because individual key data is not processed. Unsupported value/range-key/range-del attributes trigger whole-file copy instead of partial copy.

## Dependencies and Integration Points
Integrates with `Reader`, `RawColumnWriter` copy helpers, `layout` attributes, object storage read handles, cache handles, table filters, and index iterators. Used by virtual/backing SSTable workflows that need fast physical subset creation.

## Risks and Edge Cases
The span is approximate because whole blocks are copied and adjacent keys may be included. Empty spans return `ErrEmptySpan` only when the index search finds no candidate blocks. Properties can overcount. Cached blocks are added as uncompressed blocks and recompressed, while uncached blocks are copied as already-encoded physical blocks. Unsupported features degrade to whole-file copy.

## Test Signals
Covered by `copier_test.go` datadriven build/iterate/copy/describe/props scenarios.
