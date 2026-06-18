# sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/mysql/json/mod.rs

Purpose: defines the binary JSON module, public JSON value/reference types, constructors, conversion hooks, creation functions, and module exports for MySQL/TiDB binary JSON.

Important APIs/types/functions: `JsonType`, `JsonRef<'a>`, `Json`, `json_array`, `json_object`, constructors such as `from_string`, `from_i64`, `from_ref_array`, `from_object`, `from_time`, `from_duration`, accessors such as `get_u64`, `get_i64`, `get_double`, `get_elem_count`, `get_literal`, `get_str`, `get_opaque_type`, `get_time`, `get_duration`, `Json::as_ref`, and re-exports for codecs, path parsing, and `ModifyType`.

Control flow: construction methods write MySQL binary JSON payloads through encoder helpers and store a `JsonType` plus bytes. `JsonRef` offers zero-copy access to typed slices with assertions guarding expected type. SQL creation helpers convert `Datum` values into JSON arrays or key/value objects, rejecting odd object arity and null member names. Conversion implementations cast JSON to float and Rust/MySQL values into JSON.

State and persistence: owned state is `Json { type_code, value: Vec<u8> }`; borrowed state is `JsonRef { type_code, value: &[u8] }`. No disk persistence. Binary bytes are the durable in-memory representation passed across codec boundaries.

Dependencies and integration points: imports binary, comparison, codec, modifier, path, serde, and JSON function submodules. Integrates with datum conversion, time/duration codecs, decimal/real conversion, `EvalContext` warning behavior, and `AsMySqlBool`.

Risks: many accessors assert type rather than returning typed errors, so callers must check `JsonType`. `AsMySqlBool` is marked TODO and currently always false. Float/decimal JSON conversion intentionally loses DECIMAL typing. Tests cover array/object creation and JSON-to-float conversion/truncation behavior.
