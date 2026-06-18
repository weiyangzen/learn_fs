# sources/object-store/rustfs/crates/ecstore/src/client/utils.rs

## Purpose
Supplies header/query classification helpers and base64 encoding/decoding utilities shared by the S3 client.

## Important APIs, types, and functions
Functions include `is_standard_query_value`, `is_storageclass_header`, `is_standard_header`, `is_sse_header`, `is_amz_header`, `is_rustfs_header`, `is_minio_header`, `base64_encode`, and `base64_decode`. Lazy maps define supported query keys, standard headers, and SSE headers.

## Control flow
Header checks lowercase keys and test membership/prefixes. `is_amz_header` accepts user metadata, grant headers, ACL, SSE headers, and checksum headers. Base64 helpers use `base64_simd::URL_SAFE_NO_PAD`.

## State and persistence behavior
The only state is lazy immutable lookup maps. No persistence.

## Dependencies and integration points
Used by checksum decoding, S3 datatype checksum handling, and likely request option/header filtering modules. Depends on `s3s` header constants and `base64_simd`.

## Risks and edge cases
`is_standard_query_value` indexes the map directly and will panic for unknown keys; other helpers use safe lookup. URL-safe no-pad base64 may be incompatible with standard AWS checksum/content-MD5 base64 expectations if used for wire headers.

## Test signals
No local tests are present. Direct tests should cover unknown query key behavior, case-insensitive header checks, SSE/amz prefixes, and base64 compatibility expectations.
