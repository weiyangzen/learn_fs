# sources/object-store/rustfs/crates/signer/src/request_signature_v4.rs

## Purpose
Implements AWS Signature Version 4 signing, presigning, trailer signing, and shared canonicalization helpers for S3 and internal STS-style signing.

## Important APIs and Functions
`SignV4Error` reports invalid header values, time failures, query encoding, URI construction, canonical UTF-8 conversion, and header value parsing. Public APIs are `try_pre_sign_v4`, `pre_sign_v4`, `try_sign_v4`, `sign_v4`, `try_sign_v4_trailer`, and `sign_v4_trailer`.

Shared helpers include `get_signing_key` (AWS4 date/region/service/aws4_request HMAC chain), `get_signature`, `get_scope`, `format_yyyymmdd`, `format_amz_datetime`, `try_get_hashed_payload`, `try_get_canonical_headers`, `get_signed_headers`, `try_get_canonical_request`, and `try_get_string_to_sign_v4`. Ignored headers are `accept-encoding`, `authorization`, and `user-agent`.

`pre_sign_v4_inner` appends `X-Amz-*` query parameters, canonicalizes the resulting request, computes a signature, and rewrites the URI with `X-Amz-Signature`. `sign_v4_inner` inserts `X-Amz-Date`, optional security token, optional trailer metadata and decoded length, optionally removes payload hash for STS, canonicalizes the request, computes Authorization, and for trailer requests calls `streaming_unsigned_v4` after adding trailer headers.

## Control Flow and State
Everything is synchronous request mutation. Static state is limited to the lazy ignored-header set. The legacy wrappers preserve non-panicking behavior by logging and returning the original request if canonicalization/signing fails.

## Integration Points
Uses `http::Request`, `http::Uri`, `HeaderMap`, `s3s::Body`, `time`, `serde_urlencoded`, `rustfs_utils::crypto::{hmac_sha256, hex, hex_sha256}`, signer constants, signer utils for host resolution and whitespace trimming, and the unsigned streaming trailer module.

## Risks
Canonical query handling sorts by key only and performs a post-hoc `+` to `%20` replacement; full AWS percent-encoding and duplicate key ordering may be incomplete. Presign builds the canonical request after including `X-Amz-Signature`, which is unusual for SigV4 and reflected in tests. `sign_v4_inner` signs with current time but builds credential scope using midnight (`t2`), which is the same date but surprising. Relative URIs with a Host header are rejected by the fallible API because canonical host resolution requires a URI host. Trailer flow computes Authorization before `streaming_unsigned_v4` mutates date/token/transfer headers, so the final signed header set must be reviewed carefully.

## Test Signals
Tests include AWS-style canonical request/string/signature examples, RustFS example signatures with host override and empty region, presigned URL examples, invalid non-UTF8 header handling, missing URI host handling, legacy non-panicking wrappers for invalid headers, STS wrapper behavior, and zero-padded date formatting.
