## sources/object-store/garage/src/api/common/signature/error.rs

Purpose: signature-specific error enum layered on top of `CommonError`.

Important APIs/types/functions: `Error::{Common, AuthorizationHeaderMalformed, InvalidUtf8Str, InvalidDigest}`, blanket `From<T>` for `CommonError`-convertible types, and `CommonErrorDerivative` impl.

Control flow: lower-level parsing/crypto/checksum helpers convert common errors into signature errors; API-specific error types later map this enum into S3/K2V errors.

State/persistence: none.

Dependencies/integration: used by all modules under `signature`; converted by K2V and S3 error layers.

Risks: variants must stay aligned with downstream `From<SignatureError>` matches. Authorization scope errors carry expected/unexpected strings that become client-visible.

Test signals: no local tests; compile-time exhaustive matches in downstream error conversions are useful signals.
