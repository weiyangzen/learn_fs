# sources/object-store/rustfs/crates/crypto/src/jwt/tests.rs

## Purpose
This file is the unit-test suite for the crypto crate's JWT wrapper. It validates that `super::encode::encode` and `super::decode::decode` interoperate for JSON claims signed with a shared secret, and that decoding rejects malformed, expired, or incorrectly signed tokens. The tests document the intended JWT behavior exposed later as `rustfs_crypto::jwt_encode` and `rustfs_crypto::jwt_decode`.

## Important APIs, Types, and Functions
The suite uses `serde_json::json!` to build arbitrary claim payloads and `time::OffsetDateTime::now_utc().unix_timestamp()` for time-sensitive `exp`, `iat`, and `nbf` claims. It exercises the opaque `encode(secret, &claims) -> Result<String, _>` API and `decode(&jwt_token, secret) -> Result<TokenData<Value>, _>`, then checks `decoded.claims` and `decoded.header`.

## Control Flow
Most tests follow a common flow: create claims, sign them with a byte-slice secret, decode with either the same or a different secret, and assert success or failure. Negative tests iterate invalid token strings, use expired `exp` claims, or change the secret. Header tests split the token into three dot-separated segments and assert the decoded algorithm is `jsonwebtoken::Algorithm::HS512`.

## State and Persistence
The file has no persistent state. It depends on wall-clock time, so tokens with `exp` close to `now` could be flaky if the clock changes, but the chosen offsets are large enough for normal test execution. Deterministic encoding is asserted only with fixed integer timestamps.

## Dependencies and Integration Points
The tests depend on the local `jwt` module, `serde_json`, `time`, and the `jsonwebtoken` header type. They are compiled as child module tests of `crypto/src/jwt.rs`, not through the public crate re-exports directly, but they protect the same implementation that `crypto/src/lib.rs` exports.

## Risks and Edge Cases
The suite confirms expiration validation but explicitly documents that future `iat` is not rejected by the current implementation. It does not test `aud`, `iss`, clock skew, missing `exp`, non-object claims, or algorithm-confusion attempts. The acceptance of very short secrets is tested, which is useful compatibility coverage but also shows no minimum HMAC secret strength is enforced here.

## Test Signals
Strong positive signals include round trips for nested JSON, arrays, booleans, numeric values, special characters, unicode strings, and a 10 KB payload. Negative signals include wrong-secret rejection, malformed token rejection, and expired token rejection. The file itself is the test signal for JWT signing and validation behavior.
