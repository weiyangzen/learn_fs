<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/crypto/src/jwt/decode.rs -->
# sources/object-store/rustfs/crates/crypto/src/jwt/decode.rs

## Purpose
Provides HS512 JWT decoding using a shared secret.

## Important APIs, types, and functions
`decode(token, token_secret)` returns `jsonwebtoken::TokenData<Claims>` or crate `Error`, using `DecodingKey::from_secret` and `Validation::new(Algorithm::HS512)`.

## Control flow
The function delegates signature and claim validation to `jsonwebtoken::decode` with HS512 validation.

## State and persistence behavior
No state.

## Dependencies and integration points
Integrates with `jwt::Claims`, crate error conversion, and authentication/session token consumers.

## Risks and edge cases
Default `Validation::new` behavior must match product requirements for exp/aud/issuer. Secret length/entropy is not checked here. Algorithm is fixed to HS512, so tokens using other algorithms fail.

## Test signals
Tests should cover valid HS512 tokens, bad signatures, expired tokens if exp validation is expected, malformed JSON claims, and wrong algorithm headers.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/crypto/src/jwt/decode.rs -->
