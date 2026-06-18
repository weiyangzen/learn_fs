# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/token/ShortLivedTokenSecretManager.java

## Purpose

`ShortLivedTokenSecretManager` is the generic signing base for short-lived token identifiers. It centralizes token lifetime calculation, signing with the current managed secret key, and construction of Hadoop `Token<T>` objects.

## Important APIs, Types, and Functions

The type parameter is bounded by `ShortLivedTokenIdentifier`. `createPassword(T)` gets `SecretKeySignerClient.getCurrentSecretKey()`, stores that key ID into the token identifier, and returns `ManagedSecretKey.sign(tokenId)`. `getTokenExpiryTime()` returns now plus configured max lifetime. `generateToken(T)` wraps identifier bytes, password, kind, and service in a Hadoop token. `setSecretKeyClient` exists for integration tests.

## Control Flow

Callers construct or receive a populated identifier, then call `generateToken`. The manager signs after setting the secret key ID, so verifiers can later fetch the exact key by ID before checking the signature.

## State and Persistence Behavior

The class stores token lifetime and the signer client reference. It persists no token state. Persistent security state lives in the secret-key subsystem and in serialized token identifiers given to clients.

## Dependencies and Integration Points

It depends on `ManagedSecretKey`, `SecretKeySignerClient`, Hadoop `Token`, and `Text`. Concrete subclasses such as block and container token managers provide domain-specific identifiers and services.

## Risks and Edge Cases

Clock skew affects effective expiry. Replacing the signer client in tests mutates shared manager state, so production code should not call it. If the current secret key rotates immediately after issuance, verifiers must still retain the old key until all tokens expire.

## Test Signals

Check generated token fields, key ID mutation before signing, expiry timing, behavior with a fake signer client, and verification compatibility across secret-key rotation windows.
