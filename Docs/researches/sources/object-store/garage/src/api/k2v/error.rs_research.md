## sources/object-store/garage/src/api/k2v/error.rs

Purpose: K2V API error type and HTTP/JSON error response implementation.

Important APIs/types/functions: `Error` enum, `commonErrorDerivative!(Error)`, `From<SignatureError>`, `Error::code`, and `ApiError for Error`.

Control flow: signature errors are converted variant-by-variant. `http_status_code` maps common errors through `CommonError`, missing keys to `404`, not acceptable to `406`, and malformed auth/base64/UTF8/digest/causality to `400`. `http_body` emits `CustomApiErrorBody` as pretty JSON. `add_http_headers` always adds JSON content type and wildcard CORS origin.

State/persistence: none.

Dependencies/integration: consumed by `generic_server::ApiError`; used throughout K2V route handlers.

Risks: wildcard CORS on error responses may expose error details cross-origin by design. `InvalidCausalityToken` code string is `"CausalityToken"`, which may be a compatibility contract. Pretty JSON serialization fallback omits region/path fields.

Test signals: no local tests; compile-time conversions and API error integration are primary signals.
