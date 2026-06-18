# sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/mysql/json/json_depth.rs

## Purpose
`json/json_depth.rs` implements JSON document depth calculation. It provides the behavior behind MySQL/TiDB JSON depth functions by recursively counting the maximum nesting level of arrays and objects.

## Important APIs, Types, and Functions
The public API is `JsonRef::depth(&self) -> Result<i64>`. The private recursive helper `depth_json(j: &JsonRef<'_>) -> Result<i64>` handles traversal. It uses `JsonType`, `get_elem_count`, `object_get_val`, and `array_get_elem`.

## Control Flow
For scalar JSON values, `depth_json` returns `0 + 1`, so scalars have depth 1. For objects, it iterates every value, recursively computes child depth, tracks the maximum, and returns `max_depth + 1`. Arrays follow the same pattern over elements. Empty arrays and objects have no children, so their max child depth remains zero and their depth is 1.

## State and Persistence Behavior
The calculation is read-only and keeps only stack-local recursion state. It does not persist or mutate anything. Returned depth is an `i64`, but traversal depth is bounded in practice by the binary JSON input and call stack.

## Dependencies and Integration Points
The module depends on `JsonRef`, `JsonType`, shared `Result`, and binary JSON navigation helpers. It integrates with scalar JSON functions and inherits binary layout assumptions from `binary.rs`.

## Risks and Edge Cases
Deeply nested JSON can cause deep recursion and potential stack pressure. Malformed binary JSON can make `object_get_val` or `array_get_elem` return errors or panic through lower-level slicing. Empty containers intentionally return depth 1, which matches MySQL semantics but can surprise callers expecting zero for empty documents.

## Test Signals
Tests cover null, booleans, numbers, strings, empty arrays/objects, flat arrays/objects, mixed arrays with objects, and deeply nested object/array structures up to depth 6.
