# sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/mysql/json/json_length.rs

Purpose: implements MySQL `JSON_LENGTH` over binary JSON.

Important APIs/types/functions: private `JsonRef::len` returns object/array element count or `1` for scalars; public `JsonRef::json_length` adds optional path behavior. It depends on `JsonType`, `get_elem_count`, `PathExpression`, and `JsonRef::extract`.

Control flow: without a path, the function always returns `Some(length)`. With exactly one wildcard path it returns `Ok(None)`. Otherwise it extracts using the provided path list and maps an existing target to that target's length.

State and persistence: no persistence and no mutation. All state is local and derived from the encoded JSON slice.

Dependencies and integration points: consumes path parser flags and shared extraction logic. It participates as an attribute function in the JSON codec API.

Risks: the special wildcard `None` behavior is compatibility-sensitive. Multiple path expressions are passed through to `extract`; because `extract` may auto-wrap multiple matches as an array, length can become count of matched roots rather than length of an individual target. Tests cover scalars, arrays, objects, path selection, wildcard-to-None, and missing targets.
