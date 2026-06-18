# sources/object-store/rustfs/crates/iam/src/utils.rs

Purpose: compact JWT helper module for IAM credentials and session tokens.

Important APIs: `generate_jwt<T: Serialize>` signs arbitrary serializable claims with HS512. `extract_claims<T: DeserializeOwned + Clone>` verifies and decodes HS512 tokens using normal jsonwebtoken validation. `extract_claims_allow_missing_exp<T>` verifies HS512 while clearing `required_spec_claims`, allowing tokens without an expiration claim.

Control flow and state: all functions are pure wrappers around `jsonwebtoken` and keep no local state. Encoding builds a `Header` with `Algorithm::HS512` and an `EncodingKey` from the secret bytes. Decoding builds a `DecodingKey` from the same secret and validates the signature/claims. The missing-exp variant changes validation requirements before calling decode.

Dependencies and integration: used by IAM `sys.rs` and manager utilities to create and parse service-account and STS credential JWTs. It depends on `jsonwebtoken`, `serde`, and `HashSet`.

Risks: secrets are raw shared HMAC keys, so callers must protect secret material and choose sufficient entropy. The missing-exp decoder is intentionally permissive and should only be used for account types that allow non-expiring tokens. Algorithms are fixed to HS512, which is simple but means all issuers/verifiers need symmetric secret access.

Test signals: unit tests cover token shape, different secrets/claims producing different tokens, valid decode, wrong secret failure, invalid token failure, round-trip header algorithm, empty claims, and special characters.
