# sources/object-store/rustfs/crates/trusted-proxies/src/error/mod.rs

Purpose: Aggregates trusted-proxies error types and defines the crate-wide `AppError`.

Important APIs: Re-exports `ConfigError` and `ProxyError`; defines `AppError::{Config, Proxy, Cloud, Internal, Io, Http}`, constructors `cloud/internal/http`, recoverability classification, `ApiError` alias, and `From<AppError> for (StatusCode, String)`.

Control flow: Recoverability delegates to `ProxyError::is_recoverable` and treats config/cloud/io/http as recoverable while internal is not. HTTP status mapping returns bad request for config/proxy, service unavailable for cloud, internal server error for internal/io, and bad gateway for HTTP.

State and dependencies: Error-only module using `thiserror`, `http::StatusCode`, and `std::io`.

Integration points: Cloud metadata/range helpers use `AppError::cloud`; application boundaries can convert into API errors.

Risks and tests: Marking all config errors recoverable is a policy choice that may mask startup misconfiguration if used beyond fallback paths. No direct requested tests validate status mappings or recoverability.
