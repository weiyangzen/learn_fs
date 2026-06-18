# sources/distributed-fs/tahoe-lafs/src/allmydata/storage/http_common.py

## Purpose
Provides shared HTTP storage protocol constants and helpers for content types, authorization headers, operation-secret enum values, and SPKI certificate hashing.

## Important APIs, Types, and Functions
Defines `CBOR_MIME_TYPE`, `get_content_type()`, `response_is_not_html()`, `swissnum_auth_header()`, `Secrets`, `get_spki()`, and `get_spki_hash()`.

## Control Flow
Header helpers parse Twisted `Headers` with Werkzeug `parse_options_header`, construct `Authorization: Tahoe-LAFS <base64-swissnum>`, assert non-HTML responses in tests, and derive URL-safe base64 SHA-256 hashes of certificate SubjectPublicKeyInfo bytes.

## State and Persistence Behavior
No state or persistence.

## Dependencies and Integration Points
Used by both HTTP client and server. Depends on cryptography certificate serialization, hashlib SHA-256, Twisted headers/response interfaces, and Werkzeug header parsing.

## Risks and Edge Cases
`response_is_not_html()` is test-oriented and asserts for non-404 HTML responses. `get_content_type()` uses only the first content-type header value. SPKI hashes strip padding for NURL embedding, so callers must consistently use the same encoding.

## Test Signals
`test_storage_http.py::HTTPUtilities` covers content-type parsing, while HTTP auth/client/server tests exercise `Secrets`, `swissnum_auth_header()`, and non-HTML response assertions. `test_storage_https.py` covers SPKI-pinning integration.
