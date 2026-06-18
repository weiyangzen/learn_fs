# sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/mysql/json/json_type.rs

Purpose: implements MySQL `JSON_TYPE` string classification for binary JSON.

Important APIs/types/functions: `JsonRef::json_type` returns static byte-string constants such as `OBJECT`, `ARRAY`, `INTEGER`, `UNSIGNED INTEGER`, `DOUBLE`, `STRING`, `BOOLEAN`, `NULL`, `DATE`, `DATETIME`, `TIME`, `BLOB`, `BIT`, or `OPAQUE`.

Control flow: the method matches `JsonType`. Literal values distinguish booleans from null by `get_literal()`. Opaque values inspect `FieldTypeTp` and classify blob/string families as `BLOB`, bit as `BIT`, and unknown or unsupported types as `OPAQUE`. Timestamp maps to `DATETIME`.

State and persistence: no state beyond reading type code and opaque metadata from the borrowed JSON value.

Dependencies and integration points: depends on `FieldTypeTp`, `JsonType`, and opaque metadata accessors from `mod.rs`. Used by expression evaluation for SQL `JSON_TYPE`.

Risks: opaque classification depends on valid embedded field type. Any new JSON/opaque variants need this match updated to avoid generic `OPAQUE`. Tests cover standard object, array, signed/unsigned/double numeric boundaries, strings, booleans, and null; opaque/time classifications are not locally tested here.
