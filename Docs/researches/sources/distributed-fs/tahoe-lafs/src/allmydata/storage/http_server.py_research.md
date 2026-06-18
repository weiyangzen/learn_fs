# sources/distributed-fs/tahoe-lafs/src/allmydata/storage/http_server.py

## Purpose
Implements the HTTP storage server API for Tahoe storage operations, including authorization, CBOR validation/encoding, immutable upload lifecycle, mutable RTW operations, lease renewal, range reads, corrupt-share notifications, TLS endpoint wrapping, and NURL construction.

## Important APIs, Types, and Functions
Important definitions include `ClientSecretsException`, `_extract_secrets()`, `_authorization_decorator()`, `_authorized_route()`, `StorageIndexUploads`, `UploadsInProgress`, `StorageIndexConverter`, `_HTTPError`, `_ReadAllProducer`, `_ReadRangeProducer`, `read_range()`, `_add_error_handling()`, `read_encoded()`, `HTTPServer`, `_TLSEndpointWrapper`, `build_nurl()`, and `listen_tls()`.

## Control Flow
Each route is decorated to clear default HTML content type, verify swissnum Authorization, extract required `X-Tahoe-Authorization` secrets, and log request/response metadata. Immutable creation validates CBOR allocate requests, calls `StorageServer.allocate_buckets()`, and tracks returned `BucketWriter`s by upload secret. PATCH writes stream request content into the bucket at the Content-Range offset, returning remaining ranges and closing on completion. Reads use producer-backed range/full-body streaming. Mutable RTW validates CBOR, converts vectors to storage-server tuples, and returns read data plus success. TLS helpers wrap endpoints and generate `pb`/`pb+...` NURLs with SPKI hash userinfo and swissnum path.

## State and Persistence Behavior
`HTTPServer` owns in-memory `UploadsInProgress`, removed via a bucket-writer close handler when uploads finish, abort, or time out. Durable share data and leases are persisted by the underlying `StorageServer`, `BucketWriter`, and mutable share APIs. CBOR responses may be spooled to a temporary file before producer streaming.

## Dependencies and Integration Points
Depends on Klein/Twisted web server, pycddl, cbor utilities, Tahoe `StorageServer`, immutable `BucketWriter`, base32 storage-index conversion, werkzeug range/accept parsing, TLS certificate loading, and Tahoe secret/auth helpers. It is the server-side counterpart to `storage/http_client.py`.

## Risks and Edge Cases
The immutable allocate endpoint intentionally leaks existence of parallel in-progress uploads for the same storage index/share. Mutable RTW accepts very large bodies (`2**48` max) but uses mmap/off-thread validation to limit copies. Range support is intentionally narrow: one byte range with explicit end. Upload content length mismatch hits assertions. Secret extraction requires exact required-secret sets and 32-byte lease secrets.

## Test Signals
`test_storage_http.py` extensively covers auth failures, secret validation, storage-index converter, schema validation, MIME negotiation, immutable upload conflicts/aborts/timeouts/listing, mutable RTW/listing/wrong write enabler, corrupt-share reporting, lease renewal, and read range behavior. `test_storage_https.py` covers `_TLSEndpointWrapper` and TLS policy interactions.
