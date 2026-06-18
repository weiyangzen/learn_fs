# sources/distributed-fs/tahoe-lafs/src/allmydata/storage/http_client.py

## Purpose
Implements the Tahoe HTTP storage client transport, including TLS pinning, swissnum authorization, CBOR schema validation, immutable uploads/downloads, mutable read-test-write operations, lease renewal, and corrupt-share reporting.

## Important APIs, Types, and Functions
Important types include `ClientException`, `_LengthLimitedCollector`, `ImmutableCreateResult`, `_TLSContextFactory`, `_StorageClientHTTPSPolicy`, `StorageClientFactory`, `StorageClient`, `StorageClientGeneral`, `UploadProgress`, `StorageClientImmutables`, `WriteVector`, `TestVector`, `ReadVector`, `TestWriteVectors`, `ReadTestWriteResult`, and `StorageClientMutables`. Helpers include `_encode_si()`, `limited_content()`, `read_share_chunk()`, and `advise_corrupt_share()`.

## Control Flow
`StorageClientFactory.create_storage_client()` parses NURLs, creates a Twisted/Tor agent, pins TLS by SPKI hash, and builds a base HTTPS URL plus swissnum. `StorageClient.request()` injects Authorization and Tahoe secret headers, serializes CBOR bodies off-thread, applies timeouts, and logs via Eliot. Higher-level clients construct endpoint URLs, send requests, decode CBOR under pycddl schemas, and map HTTP status codes to typed results or `ClientException`.

## State and Persistence Behavior
Client state is connection-oriented: base URL, swissnum, treq client, HTTP connection pool, reactor clock, and optional cached Tor instance in the factory. No local storage is persisted. Remote persistence is triggered by storage-server operations such as allocate/write immutable shares, mutable RTW writes, and lease renewal.

## Dependencies and Integration Points
Depends on Twisted web client, treq, hyperlink, OpenSSL, cryptography certificates, pycddl, CBOR helpers, Range/Content-Range parsing, Eliot, Tahoe HTTP common utilities, Tor provider integration, and cputhreadpool offloading. Exposes an API used by Tahoe storage-client selection and tests.

## Risks and Edge Cases
Retry behavior is explicitly TODO for failed uploads/downloads. `limited_content()` bounds memory and silence but still buffers into `BytesIO`. TLS validation intentionally accepts self-signed/expired certs only when SPKI hash matches. Mutable RTW error reporting includes response content only for some paths. Content-Range validation is strict and treats unexpected OK responses for ranged reads as errors.

## Test Signals
`src/allmydata/test/test_storage_http.py` has extensive coverage for content-type helpers, secret extraction, authorization, schema validation, limited content length/timeouts, immutable upload/read/list/abort/conflict paths, mutable RTW/read/list paths, lease renewal, corrupt-share reporting, and shared range-read behavior. `test_storage_https.py` covers TLS policy behavior.
