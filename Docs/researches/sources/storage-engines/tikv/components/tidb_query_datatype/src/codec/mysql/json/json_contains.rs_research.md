# sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/mysql/json/json_contains.rs

## Purpose
`json/json_contains.rs` implements MySQL `JSON_CONTAINS` semantics for binary JSON values. It answers whether a source JSON document contains a target JSON document using recursive object, array, and scalar rules compatible with TiDB.

## Important APIs, Types, and Functions
The file adds `JsonRef::json_contains(&self, target: JsonRef<'_>) -> Result<bool>`. It relies on `JsonType`, binary object/array accessors (`get_elem_count`, `object_get_key`, `object_get_val`, `object_search_key`, `array_get_elem`), and JSON comparison from `comparison.rs`.

## Control Flow
If the source is an object and the target is also an object, every target key must exist in the source object and the corresponding source value must recursively contain the target value. Empty target objects are therefore contained by any object. If the source is an array and target is an array, each target element must be contained somewhere in the source array. If the source is an array and target is not an array, any source element containing the target is sufficient. For scalar source values, containment is equality according to JSON partial comparison. All other object/non-object mismatches return false.

## State and Persistence Behavior
The function is read-only and recursively traverses borrowed binary JSON. It does not allocate persistent state or mutate the document. Its behavior is used by SQL predicate evaluation.

## Dependencies and Integration Points
The module depends on `JsonRef`, `JsonType`, shared `Result`, binary navigation from `binary.rs`, and comparison from `comparison.rs`. It integrates with MySQL JSON search functions in the expression layer and with object key sorting assumptions from the binary JSON encoder because `object_search_key` is binary search.

## Risks and Edge Cases
The scalar branch calls `self.partial_cmp(&target).unwrap()`, so malformed or non-comparable JSON that yields `None` can panic. Array containment is recursive and can revisit many nested values, so deeply nested or large arrays can be expensive. Object containment depends on sorted object keys; if a binary JSON object is malformed or unsorted, key search can return false even when bytes contain the key. Duplicate target array elements are checked independently and do not consume source elements.

## Test Signals
Tests cover object subset containment, empty objects, scalar/object mismatches, arrays containing scalars and arrays, nested arrays and objects, numeric/string distinctions, object-in-array containment, negative cases, and a large integer comparison edge.
