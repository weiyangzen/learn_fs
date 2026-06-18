# sources/storage-engines/pebble/sstable/format.go

## Purpose
Defines SSTable table format versions, their capabilities, footer sizes, parsing, string conversion, and index-iterator selection.

## Important APIs, Types, and Functions
- `TableFormat` enum covers LevelDB, RocksDBv2, Pebble v1-v8, min/max supported formats, and unspecified.
- `footerSizes` maps formats to footer lengths.
- Long format comments document v4 obsolete-bit semantics and strict-obsolete correctness.
- `parseTableFormat`, `BlockColumnar`, `TieringMetadata`, `TieringColumnConfig`, `FooterSize`, `newIndexIter`, `AsTuple`, `String`, and `ParseTableFormatString` expose capabilities and conversions.

## Control Flow
Footer parsing supplies magic bytes and version to `parseTableFormat`, which validates known combinations and returns corruption errors for unsupported versions or bad magic. Feature methods gate columnar blocks at v5, tiering columns at v8, and footer sizes by format. `newIndexIter` selects row or columnar index iterators based on `BlockColumnar`.

## State and Persistence Behavior
The enum values themselves are not serialized. Disk format is represented by magic/version tuples and footer sizes. Format capabilities drive whether writers emit row/columnar blocks, checked footers, columnar metaindex/properties, blob handles, and tiering metadata.

## Dependencies and Integration Points
Used by readers, writers, layout decoding/formatting, options defaults, properties serialization, and value/blob/tiering feature gates. Depends on `base`, `blockiter`, `colblk`, and `rowblk`.

## Risks and Edge Cases
Adding a format requires updating enum order, footer sizes, tuple/string parsing, tests, and feature gates. Strict-obsolete semantics are correctness-sensitive for disaggregated/foreign SSTable reads. Unsupported versions must return corruption errors, not silently downgrade.

## Test Signals
`format_test.go` validates magic/version round trips and error messages for unsupported versions and bad magic.
