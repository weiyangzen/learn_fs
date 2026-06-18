# sources/object-store/rustfs/crates/protocols/src/swift/cors.rs

## Purpose
This file implements Swift CORS support for containers. It loads CORS configuration from Swift container metadata, injects CORS headers into normal responses, handles browser preflight `OPTIONS` requests, and exposes a convenience check for whether CORS is configured.

## Important APIs, Types, And Functions
- `CorsConfig` stores `allow_origin`, `max_age`, `expose_headers`, and `allow_credentials`.
- `CorsConfig::load(account, container_name, credentials)` calls `container::get_container_metadata` and parses `x-container-meta-access-control-*` custom metadata keys.
- `CorsConfig::is_enabled` returns true when an allowed origin is configured.
- `CorsConfig::inject_headers(response, request_origin)` adds `access-control-allow-origin`, `access-control-expose-headers`, and `access-control-allow-credentials` when applicable.
- `handle_preflight(account, container_name, credentials, request_headers)` builds the `OPTIONS` response, adds allowed methods, max age, echoed request headers, and Swift transaction id headers.
- `is_enabled(account, container_name, credentials)` loads configuration and converts load errors to `Ok(false)`.

## Control Flow
Loading is metadata-driven. `allow_origin` is copied directly from `x-container-meta-access-control-allow-origin`; `max_age` is parsed as `u64` and ignored on parse failure; `expose_headers` is split on commas and trimmed; `allow_credentials` is true only when the metadata value lowercases to `"true"`.

Header injection is a no-op unless CORS is enabled. A configured wildcard origin always emits `access-control-allow-origin: *`. A specific configured origin is emitted only when the request `Origin` header is present and exactly equals the configured value. Expose headers are joined with comma-space. Credentials are emitted whenever enabled, independent of whether an allow-origin header was actually inserted.

Preflight handling loads config, rejects unconfigured containers with `Forbidden`, extracts `Origin`, creates an empty `200 OK` response, injects CORS headers, adds a fixed Swift method list, adds max age if configured, echoes `Access-Control-Request-Headers` as `Access-Control-Allow-Headers`, and appends `x-trans-id` plus `x-openstack-request-id`.

## State And Persistence Behavior
This file is read-only with respect to persistent state. CORS configuration is persisted elsewhere as Swift container custom metadata, which `container.rs` stores as `swift-meta-*` bucket tags. `cors.rs` only loads and interprets those metadata values and mutates outgoing HTTP response headers.

## Dependencies And Integration Points
The module depends on `container::get_container_metadata`, `SwiftError`/`SwiftResult`, axum/http header and response types, `s3s::Body`, `rustfs_credentials::Credentials`, `tracing`, and transaction id generation from `super::handler`.

It integrates with Swift object/container handlers that need to answer preflight requests or add CORS headers to normal responses.

## Risks And Edge Cases
- Specific origins require exact string equality; there is no list parsing, wildcard subdomain matching, normalization, or case folding.
- `allow_credentials` can be emitted with wildcard origin, a combination browsers reject for credentialed requests.
- If a specific origin is configured but the request origin does not match, `allow_credentials` and expose headers may still be added without `allow-origin`.
- `is_enabled` maps all load errors, including storage errors, to `false`, which can hide backend failures.
- Invalid `max_age` values are silently ignored.
- Echoing requested headers trusts the request header value as long as it is syntactically accepted by the HTTP library; no configured allow-list is enforced here.

## Test Signals
Unit tests cover default disabled config, enabled config, wildcard origin injection, exact-origin match and mismatch, expose-header joining, credentials header injection, disabled no-op behavior, and simple expose-header parsing. There are no async tests for `CorsConfig::load`, preflight response construction, transaction id headers, forbidden behavior when CORS is absent, or storage-error masking in `is_enabled`.
