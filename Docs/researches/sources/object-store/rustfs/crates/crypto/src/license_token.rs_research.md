# sources/object-store/rustfs/crates/crypto/src/license_token.rs

## Purpose
This module defines RustFS license-token encoding and verification. It keeps legacy RSA encryption/decryption helpers for compatibility but marks them deprecated, while the preferred flow signs a JSON token with a private key and verifies it with only a public key.

## Important APIs, Types, and Functions
`Token` is a serializable structure with `name` and `expired` fields. Deprecated `gencode` encrypts serialized token JSON with an RSA public key using PKCS#1 v1.5 encryption, and deprecated `parse` decrypts with a PKCS#8 private key. `sign_license_token` serializes `Token`, signs the JSON payload using RSA-PSS with SHA-256 via `BlindedSigningKey`, concatenates `signature || payload`, and base64url-encodes without padding. `parse_signed_license_token` decodes, determines signature length from the RSA public key size, verifies the RSA-PSS signature, and deserializes the payload. `parse_license_with_public_key` is a compatibility alias for signed parsing.

## Control Flow
Signing parses the private PEM, signs the JSON payload with randomness, appends payload bytes after the signature, then encodes the combined bytes. Verification decodes the outer token, parses the public PEM, splits the buffer by the key's signature length, rejects missing payloads, verifies before deserializing, and returns a `Token` only after signature validation succeeds.

## State and Persistence
The module is stateless. Token persistence is external and represented as an encoded string. The `expired` timestamp is stored but not enforced by the parser; callers must check expiration after verification.

## Dependencies and Integration Points
The module depends on `rsa`, `serde`, `serde_json`, `rand`, and `base64_simd`. It is re-exported by `crypto/src/lib.rs` for consumers that need license issuance or verification. Runtime services can use public-key parsing without private key material.

## Risks and Edge Cases
The signed format has no explicit version, key id, algorithm marker, or payload length field, so future format migration would need out-of-band handling. RSA-PSS signing is randomized, so repeated signing of the same token will produce different strings. Legacy `gencode`/`parse` use PKCS#1 v1.5 encryption and require private-key parsing at verification time, which is why they are deprecated. Expiration is not checked inside verification.

## Test Signals
Unit tests generate 2048-bit keys, verify signed round trips, verify legacy encrypted round trips, reject tampered payloads, reject invalid base64-like tokens, reject invalid signing keys, and assert the source file does not embed a private key marker. Tests cover integrity and key parsing, but not expiration enforcement or cross-key rejection.
