# sources/object-store/garage/src/garage/tests/common/custom_requester.rs

Purpose: This helper sends manually constructed S3 and K2V HTTP requests that the AWS SDK cannot easily express, especially for unusual SigV4 payload modes, unsigned headers, virtual-host style hosts, presigned-like edge cases, and K2V-specific requests.

Important APIs and types: `CustomRequester`, `RequestBuilder`, `BodySignature`, `query_param_to_string`, `to_streaming_body`, and `to_streaming_unsigned_trailer_body` are key. `BodySignature` supports `Unsigned`, `Classic`, AWS streaming signed chunks, and streaming unsigned payload trailers. Requests use Hyper, `garage_api_common::signature`, HMAC-SHA256, and collected full bodies.

Control flow: `CustomRequester::new_s3/new_k2v` bind a key, base URI, service name, and Hyper client. `RequestBuilder` accumulates method, path, query params, signed/unsigned headers, body, body signature type, and path-style versus vhost-style host. `send` constructs host/path, computes canonical SigV4 headers and body hash marker, signs the canonical request, optionally rewrites the body into AWS chunked streaming format, sends the request, collects the response body, and returns a full response.

State and persistence behavior: The helper has no persistent state. It uses the test key to sign requests and can cause server-side object/K2V mutations depending on the request. It keeps no cookies or connection state beyond Hyper's client.

Dependencies and integration points: It integrates with Garage's internal SigV4 canonicalization code, Hyper HTTP client, `chrono`, HMAC/SHA-256, and test `Instance` endpoints. It is essential for K2V tests, streaming signature tests, CORS preflights, and custom S3 requests.

Risks: The helper comments note that path and query parameters are not URL-encoded in builder input before URI assembly, so tests involving reserved/control characters may be impossible or misleading through this path. Streaming content length is computed by generating a dummy body first, which is acceptable for tests but inefficient. Header handling splits signed and unsigned headers, so misuse can accidentally test an unsigned header path.

Test signals: K2V API tests, streaming SigV4 tests, S3 CORS direct tests, and presigned request execution all rely on this helper. Passing tests validate both Garage's server behavior and the helper's request signing fidelity.
