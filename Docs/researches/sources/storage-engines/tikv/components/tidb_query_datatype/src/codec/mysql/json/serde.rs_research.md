# sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/mysql/json/serde.rs

Purpose: bridges binary `Json`/`JsonRef` with Serde JSON parsing and MySQL-style string formatting.

Important APIs/types/functions: `MySqlFormatter`, `write_mysql_finite_float`, `ToStringValue for JsonRef/Json`, `Serialize for JsonRef`, `FromStr for Json`, `JsonVisitor`, and `Deserialize for Json`.

Control flow: formatter emits spaces after commas/colons and removes `+` from exponent notation. Serialization matches `JsonType`, reads binary payloads, and serializes objects/arrays recursively. Opaque values become a `base64:typeN:...` string. Temporal values are rendered as strings with maximized fsp. Deserialization visits serde values and constructs binary JSON; unsigned integers below `i64::MAX` are stored as signed, larger values as unsigned.

State and persistence: no persistence. Serialization allocates a `Vec<u8>` writer and creates strings; deserialization constructs owned `Json` bytes.

Dependencies and integration points: depends on serde, serde_json, base64, `ToStringValue`, binary accessors, time/duration formatting, and `FieldTypeTp`. `Json::from_str` and `Display` flow through this module.

Risks: `object_get_key` is unwrapped as UTF-8 during serialization, so invalid key bytes can panic. Serde parsing chooses f64 for numbers outside integer ranges. Opaque encoding is string-based and must remain compatible with TiDB. Tests cover parsing, illegal JSON, numeric boundary storage, MySQL-style formatting, and opaque base64 rendering.
