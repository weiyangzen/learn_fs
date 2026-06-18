# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/security/token/TokenVerifierTests.java

## Purpose

This abstract base class defines common behavioral tests for `ShortLivedTokenVerifier` implementations, shared by block and container token verifiers.

## Important APIs, Types, And Functions

Subclasses provide `newTestSubject`, `tokenEnabledConfigKey`, `unverifiedRequest`, `verifiedRequest`, and `newTokenId`. The base uses `SecurityConfig`, `SecretKeyVerifierClient`, `ManagedSecretKey`, `ShortLivedTokenSecretManager`, Hadoop `Token`, and nested `MockTokenManager`.

## Control Flow

Tests construct enabled or disabled security configs, mock secret-key lookup/verification behavior, generate tokens with fixed mock passwords, and call `TokenVerifier.verify`. They assert skipped verification when disabled or for unrelated commands, and rejection for expired secret keys, unknown key IDs, invalid signatures, and expired tokens. A final test accepts a valid token.

## State And Persistence

State is in-memory token IDs, mocked secret keys, and generated Hadoop tokens. No persistence is used. `SECRET_KEY_ID` is a static random UUID used by subclass token IDs.

## Dependencies And Integration Points

The base ties verifier implementations to HDDS security config keys, short-lived token identifier expiry semantics, and symmetric secret-key verification.

## Risks

Because signatures are mocked, the base checks verifier orchestration rather than cryptographic correctness. Subclasses must ensure their `verifiedRequest` truly requires their token type.

## Test Signals

Signals include no key lookup for disabled/unrelated cases, `BlockTokenException` messages for expired key, missing key, invalid signature, and expired token, plus no exception for valid token verification.
