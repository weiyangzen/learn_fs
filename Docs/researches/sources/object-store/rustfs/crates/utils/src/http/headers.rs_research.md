# sources/object-store/rustfs/crates/utils/src/http/headers.rs

## Purpose
Centralizes HTTP/S3 header constants and classification helpers used across RustFS object APIs, metadata handling, signing, encryption, object lock, restore, checksum, replication, and Snowball import paths.

## Important APIs, Types, And Functions
The file exports a large constant catalog for standard HTTP headers, S3 `x-amz-*` headers, SSE/SSE-C headers, request IDs, checksums, object attributes, tagging, object lock, and Snowball compatibility keys. `HeaderExt` adds `lookup` to `HashMap<String, String>`, checking the given name, lowercase form, and Train-Case form. Static `LazyLock<HashMap<String, bool>>` tables hold supported response query values, metadata-copy headers, and SSE headers. Public predicates include `is_standard_query_value`, `is_storageclass_header`, `is_standard_header`, `is_sse_header`, `is_amz_header`, `is_rustfs_header`, and `is_minio_header`.

## Control Flow And State
Runtime state is limited to lazily initialized immutable lookup tables. Classifiers normalize input to lowercase before table checks or prefix checks. `HeaderExt::lookup` tries three concrete spellings rather than scanning all map keys.

## Dependencies And Integration Points
Uses `convert_case` for Train-Case key generation and is re-exported by the HTTP module. `obj/metadata.rs` imports the RustFS/MinIO/internal classification helpers to filter user metadata. The constants are integration glue for S3-compatible request parsing, response emission, and metadata persistence.

## Risks And Test Signals
The constant list is broad but not self-validating; drift against AWS S3 behavior or internal callers is possible. `HeaderExt::lookup` can miss uncommon casing because it does not compare all keys case-insensitively. There are no local unit tests in this file, so coverage is indirect through consumers such as object metadata filtering.
