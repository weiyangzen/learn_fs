# sources/object-store/rustfs/crates/protocols/src/swift/errors.rs

## Purpose
`errors.rs` centralizes Swift-specific error variants and HTTP response conversion. It provides the `SwiftError` enum and `SwiftResult<T>` alias used across the Swift protocol modules.

## Important APIs, Types, And Functions
`SwiftError` models common Swift/HTTP failures: bad request, unauthorized, forbidden, not found, conflict, payload too large, unprocessable entity, too many requests, internal server error, not implemented, and service unavailable. `fmt::Display` formats plain text messages. `status_code` maps variants to `StatusCode`. `generate_trans_id` creates timestamp-based transaction IDs. The `IntoResponse` implementation builds text responses with `x-trans-id` and `x-openstack-request-id`, and adds rate-limit headers for `TooManyRequests`.

## Control Flow
Protocol modules return `SwiftResult<T>`. When an error reaches Axum-compatible response conversion, it becomes a plain text response with Swift/OpenStack request IDs. Rate limit errors are special-cased to include `x-ratelimit-limit`, `x-ratelimit-remaining`, `x-ratelimit-reset`, and `retry-after`.

## State, Persistence, And Dependencies
There is no persisted state. The only dynamic value is a transaction id derived from current Unix microseconds. Dependencies are Axum HTTP/status/response traits and standard formatting.

## Integration Points
Every listed Swift module imports `SwiftError` directly or through `SwiftResult`. `handler.rs` also has a separate `swift_error_to_response` function that duplicates most mapping logic instead of using `IntoResponse`; this means rate-limit headers can be lost on handler errors because the handler-local converter maps `TooManyRequests` to a generic body.

## Risks And Test Signals
The timestamp transaction id can collide under high concurrency and differs from DLO's UUID-based id. Error bodies include internal strings from callers, so modules must sanitize storage errors before constructing `SwiftError::InternalServerError`. There are no local tests in this file; coverage is indirect through callers and rate-limit tests.
