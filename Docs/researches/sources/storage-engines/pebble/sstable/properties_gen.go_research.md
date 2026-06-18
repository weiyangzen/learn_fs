# sources/storage-engines/pebble/sstable/properties_gen.go

## Purpose
`properties_gen.go` is generated code for serializing, deserializing, and rendering the `Properties` structure used by Pebble SSTables. It maps well-known RocksDB-compatible and Pebble-specific property keys to typed fields, tracks which fields were present in the on-disk properties block, encodes properties back into block key/value form, and renders a stable human-readable string.

## Important APIs, Types, and Functions
- `(*Properties).load(iter.Seq2[[]byte, []byte]) error` consumes decoded property key/value pairs and populates the `Properties` receiver.
- `(*Properties).encodeAll() map[string][]byte` emits all persistent property key/value pairs, including user properties, using the on-disk byte encodings expected by SSTable writers.
- `(*Properties).isLoaded(bit int) bool` tests the generated `Loaded` bit vector.
- `(*Properties).String() string` formats loaded or non-zero fields, then user properties in sorted order.
- `_bit_*` constants define stable bit positions for every generated property field, with `_numPropBits` sizing the encoded map.

## Control Flow
`load` clears `p.Loaded`, iterates through property pairs, switches on the string property key, decodes integer fields with `binary.Uvarint`, fixed-width `IndexType` with `binary.LittleEndian.Uint32`, booleans from single-byte `"1"`, and string fields from interned byte slices. Unknown keys are treated as user properties unless present in `ignoredInternalProperties`.

`encodeAll` allocates a result map sized for known plus user properties, uses a reusable scratch allocation buffer, and inserts mandatory properties unconditionally while optional properties are omitted when they equal their zero value. Numeric properties are varint encoded; `IndexType` is little-endian; boolean properties encode as `"0"` or `"1"` when non-default.

`String` mirrors the generated property order. It prints a field when it is non-zero/non-empty/non-false or when its loaded bit is set, which preserves explicitly present zero-valued fields. User properties are sorted with `maps.Keys` and `slices.Sorted`; non-printable values are rendered as `hex:<bytes>`.

## State and Persistence Behavior
This file defines the persistence contract for the properties block. The property names are part of on-disk compatibility, including RocksDB names like `rocksdb.num.entries`, `rocksdb.comparator`, and `rocksdb.block.based.table.index.type`, plus Pebble extensions like value blocks, range-key counters, column-block schema, compression stats, obsolete-point strictness, and value-separation settings.

The `Loaded` bitset is transient state used after loading to distinguish absent fields from explicitly encoded zero values, especially for string rendering and compatibility checks. `UserProperties` persists application or collector metadata not recognized as built-in properties.

## Dependencies and Integration Points
- Uses Go `iter.Seq2` so callers can feed either row-block raw iterators or columnar key/value decoders.
- Uses `encoding/binary` for durable numeric encodings.
- Uses `intern.Bytes` to reduce allocation/copying for property names and string-like values.
- Used by `reader.go` through `decodePropertiesBlock` and `ReadPropertiesBlock`.
- Used by writer-side code through `saveToRowWriter`/property block construction, which relies on `encodeAll`.

## Risks and Edge Cases
- The generated loader ignores `binary.Uvarint` decode errors and uses zero on malformed data; corruption detection must happen in lower block decoding or surrounding validation.
- `IndexType` decoding assumes at least four bytes; malformed short values could panic unless callers validate property block shape first.
- Optional properties are omitted on zero/default encode, so old readers must tolerate absence and callers must use `Loaded` when presence matters.
- Property key strings and bit positions must stay synchronized with the `Properties` struct and generator metadata.
- User properties are stringified values; binary user values are preserved as strings but only rendered safely by `String`.

## Test Signals
`properties_test.go` loads known properties from a Hamlet fixture, round-trips a populated `Properties` value through row-block encoding, quick-checks randomized `Properties` values, and benchmarks `load`. These tests exercise the generated switch, optional-field omission, `Loaded` clearing, and sorted user-property formatting indirectly.
