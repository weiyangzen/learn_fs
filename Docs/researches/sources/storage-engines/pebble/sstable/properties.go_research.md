# sources/storage-engines/pebble/sstable/properties.go

## Purpose
Defines the SSTable `Properties` struct, derived property helpers, property serialization to row/columnar blocks, and conversion to footer attributes.

## Important APIs, Types, and Functions
- `Properties` contains RocksDB-compatible and Pebble-specific table properties with `prop` tags used by the generator.
- `NumPointDeletions` and `NumRangeKeys` compute derived counts.
- `accumulateProps` combines generated encodings with user properties and legacy RocksDB compatibility properties for pre-Pebble formats.
- `saveToRowWriter` and `saveToColWriter` serialize properties in sorted key order.
- `toAttributes` maps properties to an `Attributes` bitset for v7+ footers.
- Package variables hold common encoded legacy property values.

## Control Flow
Writers update `Properties` while building an SSTable. On close, `accumulateProps` calls generated `encodeAll`, merges user properties, conditionally adds/removes legacy RocksDB keys, then `saveToRowWriter` or `saveToColWriter` emits sorted key/value pairs depending on table format. `toAttributes` derives quick footer flags from nonzero counts and index type.

## State and Persistence Behavior
Properties are persisted in a metadata block and loaded when an SSTable is opened. Formats before v7 use a row block with large restart interval; v7+ can use columnar/compressed properties. `Loaded` records which fields were present during loading for string output, while `UserProperties` captures unrecognized non-internal keys.

## Dependencies and Integration Points
Generated methods from `properties_gen.go` are required for load/encode/string behavior. Used by `RawColumnWriter`, `Reader`, `Layout`, copier, and tests. Depends on `rowblk`, `colblk`, `maps`, `slices`, `encoding/binary`, and `unsafe` for string-to-byte conversions in columnar property writing.

## Risks and Edge Cases
Adding a property requires a supported tag type and regenerating code. `saveToColWriter` skips zero-length keys because `unsafe.StringData` cannot handle them. Copied SSTables may intentionally overcount properties. Attribute derivation must track new optional blocks and features.

## Test Signals
Covered indirectly by writer layout/properties datadriven tests, copier property tests, and generated-code compilation.
