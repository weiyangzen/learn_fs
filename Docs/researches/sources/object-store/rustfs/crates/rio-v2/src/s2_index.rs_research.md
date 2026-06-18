# sources/object-store/rustfs/crates/rio-v2/src/s2_index.rs

Purpose: this file converts between legacy `rustfs_rio::Index` values and MinIO/S2 index storage bytes. It supports both full S2 skippable index frames and MinIO's stored headerless form.

Important APIs and types: `minio_index_storage_bytes(index)` converts an `Index` to an internal `S2Index`, encodes a full index frame, then strips the chunk header, `s2idx` header, trailing size, and trailer when possible. `decode_minio_index_bytes(bytes)` first tries to load a full S2 index, then restores headers around headerless bytes and loads again, returning a legacy `Index`. Private `S2Index`, `S2IndexInfo`, and `LegacyIndexJson` model the conversion boundary.

Control flow: encoding writes chunk type `0x99`, 24-bit chunk length, `s2idx\0`, signed zig-zag varints for totals/block size/entry count, optional uncompressed deltas, predicted compressed-offset deltas, trailing total size, and `\0xdi2s`. Decoding reverses this with strict validation: buffer length, chunk type, header, nonnegative uncompressed size/block size, bounded entry count, valid flag, monotonic offsets, and trailer. `restore_index_headers` reconstructs the full frame around stored bytes.

State and persistence: there is no mutable global state. The persistent artifact is the serialized index stored with compressed object data. `MAX_INDEX_ENTRIES` limits memory growth and malformed input exposure.

Dependencies and integration points: depends on `bytes::Bytes`, `serde_json`, and `rustfs_rio::Index`. It bridges rio-v2 S2 compression with legacy index search APIs and MinIO object metadata/storage expectations.

Risks and test signals: `legacy_index_to_s2_index` depends on `Index::to_json()` field names, creating a fragile JSON-mediated conversion inside Rust code. Encoding allows `total_compressed = -1` but rejects negative uncompressed sizes. Header stripping/restoring must stay byte-for-byte compatible with MinIO fixture expectations. Tests cover Go-compatible signed varint examples, headerless round-trip, and unknown compressed total decoding.
