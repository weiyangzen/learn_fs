# sources/object-store/rustfs/crates/utils/src/http/metadata_compat.rs

## Purpose
Implements dual-prefix internal system metadata compatibility between RustFS `x-rustfs-internal-*` keys and MinIO `x-minio-internal-*` keys for persisted object metadata and xl.meta migration/interoperability.

## Important APIs, Types, And Functions
Exports prefix constants, many internal suffix constants for inline data, healing, compression, actual sizes, CRC, transition/tiering, free versions, purge/replica/replication status, object-lock timestamps, tagging timestamp, and replication reset. `is_internal_key`, `has_internal_suffix`, `strip_internal_prefix`, `internal_key_starts_with`, `internal_key_strip_suffix_prefix`, and `internal_key_rustfs` classify or construct keys. `insert_str`, `get_str`, `contains_key_str`, and `remove_str` operate on `HashMap<String, String>`. Byte-map equivalents support `HashMap<String, Vec<u8>>`.

## Control Flow And State
The module is stateless. String-map reads prefer RustFS then MinIO and finally scan keys case-insensitively. String removal deletes exact keys and retains away any case-insensitive matches. Byte-map helpers only use exact key lookup/removal.

## Dependencies And Integration Points
Uses only `std::collections::HashMap`. It is re-exported through `http/mod.rs` and is directly relevant to object metadata persistence, replication, healing, transition, and MinIO-compatible imports.

## Risks And Test Signals
Writing both prefixes duplicates persisted metadata and requires consumers to handle paired values consistently. Byte-map helpers do not perform case-insensitive fallback, unlike string helpers. Tests cover prefix classification, suffix detection, and mixed-case MinIO string metadata lookup/removal, but not byte-map casing or conflict resolution when RustFS and MinIO values differ.
