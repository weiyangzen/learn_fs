# sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/mysql/json/binary.rs

## Purpose
`json/binary.rs` provides low-level navigation over TiKV/TiDB binary JSON buffers. It lets `JsonRef` read array elements, object keys and values, object key positions, value-entry payloads, literal values, raw pointer identity, and encoded length without materializing a new JSON document.

## Important APIs, Types, and Functions
All APIs are implemented on `JsonRef<'a>`. `array_get_index` converts JSON path array indexes from either left or right into a zero-based element index. `array_get_elem` reads the value entry for an array element. `object_get_key` reads a key entry and returns the raw key slice. `object_get_val` reads the value entry corresponding to an object key. `object_search_key` performs binary search over sorted object keys. `val_entry_get` decodes a value-entry type plus offset or inline literal and returns the referenced `JsonRef`. `as_ptr`, `as_literal`, and `binary_len` expose internal pointer, literal conversion, and encoded byte length.

## Control Flow
Array and object reads use layout constants from `constants.rs`. Arrays start with a header followed by value entries; objects start with a header, key entries, value entries, key bytes, and value bytes. `object_search_key` assumes keys are sorted and performs a standard lower-bound binary search using `object_get_key`.

`val_entry_get` first converts the one-byte type code into `JsonType`, reads the following little-endian `u32`, and then interprets it either as inline literal data or as an offset into `self.value()`. Fixed-width numbers, time, datetime, and duration use known byte lengths. Strings and opaque values read a varint length. Nested arrays/objects read their embedded data size from the nested header.

## State and Persistence Behavior
The module is read-only and returns borrowed slices into the original binary JSON value. It does not allocate except where errors format messages through string conversion. There is no persistence side effect, but the functions define how persisted binary JSON bytes are navigated by higher-level JSON operations.

## Dependencies and Integration Points
It depends on `codec::number::NumberCodec`, `JsonRef`, `JsonType`, binary layout constants, path expression `ArrayIndex`, `ToStringValue`, and the shared codec `Result`. It is used by JSON extraction, comparison, containment, depth, merge/modify helpers, and any scalar function that needs random access to binary JSON arrays or objects.

## Risks and Edge Cases
Most functions index directly into `self.value()` with computed offsets and lengths. They assume the `JsonRef` points to well-formed binary JSON. Corrupt value entries, unsorted object keys, invalid offsets, invalid varint lengths, or mismatched element counts can panic or return errors depending on where decoding fails. `object_get_key` has no `Result` return and will panic on malformed key offsets. `array_get_index` carefully returns `None` for right indexes beyond the array length.

## Test Signals
Tests verify type detection for common JSON literals, array element access across scalar, time, duration, nested array, string, boolean, and object values, and object key/value access for similarly mixed objects.
