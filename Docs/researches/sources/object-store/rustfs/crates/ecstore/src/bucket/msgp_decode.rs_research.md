# sources/object-store/rustfs/crates/ecstore/src/bucket/msgp_decode.rs

Purpose: Supplies private MessagePack helpers for bucket metadata compatibility. It can skip unknown values and read/write the specific msgp ext8 timestamp format used by RustFS/MinIO metadata.

Important APIs and types: `skip_msgp_value` recursively consumes one MessagePack value, including arrays and maps. `MSGP_TIME_EXT_TYPE` and `MSGP_TIME_LEN` define ext type 5 with 12 bytes of payload. `read_msgp_ext8_time` reads seconds and nanoseconds from big-endian data. `write_msgp_time` writes ext8 timestamps from `OffsetDateTime`.

Control flow and state: The helpers are stateless stream operations over `Read`/`Write`. Skip behavior first reads a marker, determines scalar payload length or recursively descends into container elements, then reads and discards payload bytes.

Dependencies and integration: Used by `metadata.rs` for unknown-field forward compatibility and timestamp encoding. Depends on `rmp::Marker`, `byteorder::BigEndian`, `time::OffsetDateTime`, and the crate `Error`/`Result` type.

Risks: `skip_msgp_value` treats `Marker::Reserved` as zero length, which may let malformed input pass farther than expected. Ext16/Ext32 skip lengths include extra bytes in addition to the type byte in a way that should be checked against the rmp marker contract if those markers appear. The time reader only accepts ext8 type 5; other timestamp encodings are handled by `metadata.rs`.

Test signals: No local tests, but `metadata_test.rs` covers ext8 writing/reading indirectly and unknown legacy formats through the full metadata decoder.
