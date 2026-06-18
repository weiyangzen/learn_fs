<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_tirocks/src/properties/mod.rs -->
# sources/storage-engines/tikv/components/engine_tirocks/src/properties/mod.rs

## Purpose
`properties/mod.rs` is the shared property codec layer for `engine_tirocks` table-property collectors. It declares property submodules, reexports collector/property types, and defines common range-index encoding/decoding helpers.

## Important APIs, Types, and Functions
Submodules include `mvcc`, `range`, `table`, and `ttl`. Public reexports include `MvccPropertiesCollectorFactory`, `RangeProperties`, `RangePropertiesCollectorFactory`, `RocksTablePropertiesCollection`, `RocksUserCollectedProperties`, and `TtlPropertiesCollectorFactory`.

`PropIndex` stores a property value and offset. `PropIndexes` wraps `BTreeMap<Vec<u8>, PropIndex>` with `new`, `into_map`, `add`, `encode`, and `decode`. The binary format is repeated `klen`, key bytes, `prop`, and `offset`, using big-endian number codec helpers.

Private `EncodeProperties` and `DecodeProperties` traits write/read raw bytes, u64 values, and encoded indexes for tirocks `UserCollectedProperties` and hash maps used in tests.

## Control Flow
Encoding iterates sorted `BTreeMap` entries and appends length/key/value fields to a buffer with bounded initial capacity. Decoding reads until the buffer is empty, reconstructing keys and indexes. Property traits map string property names to byte keys in either tirocks user properties or test hash maps.

## State and Persistence Behavior
Encoded property bytes are persisted in SST user-collected properties by collectors in submodules. The module itself has no global state.

## Dependencies and Integration Points
It depends on `codec` number/read helpers, TiKV `collections::HashMap`, and tirocks table user properties. `mvcc.rs`, `range.rs`, `ttl.rs`, and `table.rs` use these helpers to maintain format compatibility with engine traits.

## Risks and Edge Cases
`decode` trusts encoded key lengths; corrupt properties return codec/read errors. There is no version byte in the format, so changes must remain backward compatible or use new property names. The capacity heuristic caps at 1024 and is only an allocation optimization.

## Test Signals
Submodule tests exercise hash-map encoding/decoding paths. Direct tests should cover empty indexes, multiple sorted keys, truncated buffers, malformed key lengths, and compatibility with existing RocksDB property encodings.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_tirocks/src/properties/mod.rs -->
