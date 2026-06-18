# sources/distributed-fs/tahoe-lafs/src/allmydata/test/test_storage_http.py

## Purpose
This file tests the Tahoe-LAFS HTTP storage protocol client and server together with in-memory Twisted/treq infrastructure. It covers common HTTP utilities, authorization secret extraction, storage-index route parsing, client and server CBOR schema validation, request body limits/timeouts, immutable upload/download/abort APIs, mutable read/test/write APIs, shared read/range/lease/corruption APIs, and HTTP error-code mapping.

## Important APIs, Types, And Helpers
The production APIs under test include `HTTPServer`, `BaseApp`, `_authorized_route`, `_add_error_handling`, `_extract_secrets`, `Secrets`, `ClientSecretsException`, `StorageIndexConverter`, `read_encoded`, server `_SCHEMAS`, `StorageClient`, `StorageClientFactory`, `StorageClientGeneral`, `StorageClientImmutables`, `StorageClientMutables`, `ImmutableCreateResult`, `UploadProgress`, `TestWriteVectors`, `WriteVector`, `ReadVector`, `ReadTestWriteResult`, `TestVector`, `ClientException`, `limited_content`, `_encode_si`, `get_content_type`, `CBOR_MIME_TYPE`, and `response_is_not_html`.

The main test/support types are `HTTPUtilities`, `ExtractSecretsTests`, `RouteConverterTests`, `TestApp`, `CustomHTTPServerTests`, fake `Reactor`, `HttpTestFixture`, `StorageClientWithHeadersOverride`, `assert_fails_with_http_code`, `GenericHTTPAPITests`, `ImmutableHTTPAPITests`, `MutableHTTPAPIsTests`, `SharedImmutableMutableTestsMixin`, `ImmutableSharedTests`, and `MutableSharedTests`. `SECRETS_STRATEGY`, `_post_process`, `SWISSNUM_FOR_TEST`, `gen_bytes`, and `result_of` provide reusable inputs and synchronous Deferred extraction.

## Control Flow
Utility tests validate header parsing, base64 authorization secret extraction, and the werkzeug storage-index route converter. `TestApp` is a minimal Klein app with authorized routes for no-op calls, upload-secret verification, intentionally invalid version responses, bounded byte generation, never-finishing streaming responses, broken connections, and CBOR body reads.

`CustomHTTPServerTests` builds a `StorageClient` over `StubTreq(TestApp.resource())`. It checks bad swissnum decoding, malformed Tahoe authorization secrets, `_authorized_route` enforcement, client-side schema validation, `limited_content` success and oversize failures, quiescent timeout cancellation after no body data for 60 seconds, cleanup of timeout delayed calls on failed responses, CBOR default content type, and unsupported request content types.

`HttpTestFixture` creates a fake reactor with `callFromThread`, patches Twisted's global `Cooperator`, creates a real `StorageServer`, wraps it in `HTTPServer`, attaches `StubTreq`, and exposes `result_of_with_flush` to drive async endpoints by advancing fake time, flushing treq, and briefly sleeping for threadpool-backed work. The generic API tests then exercise missing/bad authentication, unsupported `Accept`, version responses, and server-side schema validation.

Immutable API tests allocate uploads, write content chunks with `Content-Range`, read back ranges, list shares only after completion, reject wrong upload secrets, allocate additional shares without overwriting in-progress uploads, reject malformed content ranges, return 404 for missing storage indexes or share numbers, keep shares separate, surface conflicts for mismatching overlapping chunks, allow reupload after timeout or abort, reject unknown/unauthorized/too-late aborts, and return 404 for lease renewal on unknown storage indexes.

Mutable API tests create shares via read/test/write vectors, read small and large data, verify combined read/test/write reads pre-write state, apply writes only when test vectors match, list mutable shares, return 404 for unknown mutable lists, and reject wrong write enablers without modifying share data. Shared mixin tests run over both immutable and mutable clients for corruption advisories, unknown-share advisory 404s, lease renew/add behavior, wrong storage-index/share read failures, invalid `Range` headers, full-body reads with no range, and `Content-Range` response headers.

## State And Persistence Behavior
Each fixture creates a temporary `StorageServer` rooted in a `TempDir`; all immutable and mutable operations persist actual Tahoe share files through the normal server implementation. Immutable uploads have in-progress writer state protected by upload secrets and timeout/abort behavior; only finished shares appear in list/read results. Mutable shares persist write-vector changes immediately when tests pass and retain their write-enabler secret for authorization.

Lease state is verified through server-side `get_leases` or `get_slot_leases`. Tests advance the fake clock to confirm renewals and new leases receive expected expiration times. Corruption advisory tests replace `StorageServer.advise_corrupt_share` with a recorder to confirm the HTTP layer passes kind, storage index, share number, and UTF-8 reason bytes.

HTTP body state is also modeled. `limited_content` accumulates streamed response bytes up to a caller-specified cap, sets delayed calls for silence timeouts, and must cancel those delayed calls on completion or failure. The fake reactor queue ensures call-from-thread callbacks are executed when time advances.

## Dependencies And Integration Points
The file depends on treq test utilities, Klein, werkzeug routing, Twisted HTTP/Headers/Clock/Cooperator/Deferreds, Hypothesis, fixtures, pycddl schema validation, `collections_extended.RangeMap`, and Tahoe CBOR utilities. It integrates the HTTP server and client modules against the real `StorageServer` rather than mocks for most protocol endpoints.

Important integration points are HTTP status codes (`401`, `400`, `406`, `416`, `404`, `409`, `405`), `Authorization` swissnum handling, `X-Tahoe-Authorization` secret headers, CBOR request/response schemas, `Range`/`Content-Range` request and response handling, immutable upload progress encoding through `RangeMap`, and shared semantics between mutable and immutable endpoints.

## Risks And Edge Cases
Covered risks include malformed auth headers, invalid base64/secret lengths, unsupported MIME types, schema drift, oversized responses, silent or failed streaming responses, missing content-type defaults, invalid storage-index path segments, in-progress upload overwrite, wrong upload keys, conflicting chunks, upload timeout/abort cleanup, late aborts, mutable conditional-write races, wrong write enablers, lease renewal on missing shares, range-header parsing, and corruption reports for unknown shares.

Residual risks include the fact that tests use in-memory treq and fake reactor traversal rather than a real TCP server. Some async paths still rely on short real sleeps in `result_of_with_flush` for backend threadpool behavior. Large mutable data is tested at 50MB, which is useful for streaming/producer behavior but can be costly in constrained CI.

## Test Signals
Passing this file signals the HTTP storage protocol can authorize, validate, encode, stream, and map errors consistently across client and server. It also confirms the HTTP layer preserves core `StorageServer` semantics for immutable and mutable shares, including upload progress, range reads, leases, aborts, conflicts, corruption advisories, and shared read behavior.
