# sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/mysql/json/json_memberof.rs

Purpose: implements MySQL 8 `MEMBER OF` semantics for binary JSON values.

Important APIs/types/functions: public `JsonRef::member_of` compares `self` with either each element of a JSON array or directly with a non-array right-hand JSON. It depends on `JsonType::Array`, `get_elem_count`, `array_get_elem`, and the `PartialOrd` implementation from JSON comparison code.

Control flow: if the right argument is an array, it loops through elements and returns true on `Ordering::Equal`; otherwise it compares the right value directly to `self`. Failure from element decoding propagates through `Result<bool>`.

State and persistence: no persistent state. The function only reads borrowed binary JSON and keeps loop counters locally.

Dependencies and integration points: integrates with `comparison.rs` ordering/equality semantics, so numeric, string, object, and array membership behavior is inherited from common JSON comparison code.

Risks: it unwraps `partial_cmp`, assuming JSON comparison always yields `Some`; NaN-like double values or future comparison changes could violate that. Array membership uses strict JSON equality, so a string containing object text is not the same as an object. Tests cover numeric/string distinctions, nested arrays, object equality versus containment, non-array direct comparison, and array-of-array membership.
