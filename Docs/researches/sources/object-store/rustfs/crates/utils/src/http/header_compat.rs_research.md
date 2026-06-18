# sources/object-store/rustfs/crates/utils/src/http/header_compat.rs

## Purpose
Provides MinIO/RustFS compatibility helpers for internal HTTP headers. Callers work with suffix constants such as `force-delete` or `source-version-id`; the module constructs `x-rustfs-*` and `x-minio-*` keys so reads accept either ecosystem and writes emit both.

## Important APIs, Types, And Functions
The public suffix constants cover force-delete, replication reset/status, source object version/mtime/etag/deletemarker, proxy/replication request markers, and replication SSEC CRC. `is_encryption_metadata_key` classifies `x-rustfs-encryption-*` and `x-minio-encryption-*` metadata case-insensitively. `get_header` reads from an `http::HeaderMap`, preferring RustFS over MinIO and returning a borrowed `Cow<str>` when the header value is valid UTF-8. `insert_header` writes both prefixes using `HeaderValue::from_bytes`. HashMap equivalents are `get_header_map`, `insert_header_map`, and `remove_header_map`.

## Control Flow And State
The module is stateless. Helper functions build string keys on demand; read flow is RustFS key first, MinIO fallback. Insert flow validates the value and parsed header names before inserting each prefixed key, silently skipping invalid inputs.

## Dependencies And Integration Points
Depends on the `http` crate for `HeaderMap`, `HeaderValue`, and `HeaderName` parsing. It is re-exported through `utils/src/http/mod.rs` and feeds object/replication paths that must interoperate with existing MinIO metadata and request headers.

## Risks And Test Signals
Risk is mainly silent failure in `insert_header` when values are not valid header bytes, plus exact-case HashMap lookup in `get_header_map` while `HeaderMap` itself is case-insensitive. Unit tests cover encryption prefix classification and HeaderMap fallback/preference basics, but not invalid header bytes or case variants in HashMap keys.
