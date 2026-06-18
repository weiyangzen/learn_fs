# sources/object-store/rustfs/crates/signer/src/request_signature_v2.rs

## Purpose
Implements AWS Signature Version 2 signing and presigning for S3-compatible requests.

## Important APIs and Functions
`SignV2Error` captures invalid headers, time formatting/components, query encoding, URI parsing/building, canonical UTF-8 conversion, header value parsing, and host resolution failures. Public APIs are `try_pre_sign_v2`/`try_sign_v2` plus legacy `pre_sign_v2`/`sign_v2` wrappers that log and return the original request on failure.

`pre_sign_v2_inner` sets an `Expires` header if absent, builds a canonical string, computes an HMAC-SHA1 signature, appends query credentials (`AWSAccessKeyId` or `GoogleAccessId` for Google Storage hosts), `Expires`, and `Signature`, and rewrites the URI. `sign_v2_inner` ensures a default RFC2822 `Date`, builds the canonical string, and inserts `Authorization: AWS access_key:signature`.

Canonical helpers write method, `Content-Md5`, `Content-Type`, `Date` or `Expires`, canonicalized `x-amz*` headers, and canonicalized resource query components from a fixed allowlist (`acl`, `uploadId`, `versionId`, etc.).

## Control Flow and State
The module consumes and returns requests. It uses local buffers and maps only; no persistent state. Time is current UTC with time replaced by midnight for Date/Expires behavior.

## Integration Points
Uses `try_get_host_addr` from signer utils, `rustfs_utils::crypto::hmac_sha1` and `hex`, `serde_urlencoded`, `hyper::Uri`, `http::HeaderValue`, and `s3s::Body`.

## Risks
V2 signing is canonicalization-sensitive. Query parsing via `HashMap` in presign may drop duplicate query keys and can reorder output. `virtual_host` is passed through but `encode_url2path` ignores it, so virtual-host-style canonical resources may be incomplete. The signature in Authorization uses URL-safe no-pad base64, which may differ from standard AWS SigV2 base64 expectations. Header canonicalization only includes values convertible to UTF-8 and silently drops invalid values.

## Test Signals
Unit tests verify presign query population, Date/Authorization insertion, canonicalized `?acl`, Authorization signature matching the injected Date, and missing optional headers.
