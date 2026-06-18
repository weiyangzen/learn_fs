# sources/object-store/rustfs/crates/keystone/src/error.rs

## Purpose
`error.rs` defines the Keystone crate's error taxonomy and result alias. It centralizes authentication, transport, parsing, configuration, authorization, and service-state failures.

## Important APIs, Types, and Functions
`pub type Result<T> = std::result::Result<T, KeystoneError>` is the crate-wide result type. `KeystoneError` variants include `InvalidToken`, `TokenExpired`, `InvalidCredentials`, `AuthenticationFailed`, `HttpError`, `ParseError`, `ConfigError`, `UnsupportedVersion`, project/user not found variants, `InsufficientPermissions`, `InternalError`, `Timeout`, and `ServiceUnavailable`. `is_retryable` classifies timeout/service-unavailable/HTTP errors. `is_auth_error` classifies token/credential/authentication failures.

## Control Flow and Integration Points
Client code maps HTTP send failures into `HttpError`, bad Keystone responses into `InvalidToken`, `InvalidCredentials`, or `AuthenticationFailed`, and JSON failures into `ParseError`. Config parsing emits `ConfigError`. Middleware uses the display string in XML error responses.

## State and Persistence Behavior
No state or persistence. Errors are displayable through `thiserror`.

## Dependencies
The only direct dependency is `thiserror::Error`.

## Risks and Edge Cases
The retry classifier treats every `HttpError` as retryable, even errors that may represent permanent DNS/TLS/configuration failures. `Timeout` and `ServiceUnavailable` variants exist but the current client often maps transport errors into `HttpError`, so specific retry semantics may be underused. Error strings can be exposed in middleware XML details after XML escaping.

## Test Signals
No direct unit tests exist for classification helpers. Behavior is indirectly exercised where other modules assert error paths.
