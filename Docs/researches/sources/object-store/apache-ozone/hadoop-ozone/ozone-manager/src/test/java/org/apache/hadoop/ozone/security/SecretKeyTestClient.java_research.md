# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/security/SecretKeyTestClient.java

## Purpose
`SecretKeyTestClient` is a test implementation of `SecretKeyClient` that supplies rotating HMAC managed secret keys for delegation token signing and verification tests.

## Important APIs, Types, and Functions
- `rotate()` generates a new `ManagedSecretKey` and stores it by UUID.
- `getCurrentSecretKey()` returns the active key.
- `getSecretKey(UUID)` returns a historical key by ID.
- `generateKey()` creates an `HmacSHA256` `SecretKey` and wraps it in `ManagedSecretKey` with one-hour validity.

## Control Flow
The constructor immediately rotates so a current key is always available. Each rotation creates a random UUID and a fresh key, updates `current`, and preserves prior keys in `keysMap`.

## State and Persistence Behavior
State is an in-memory `HashMap` and current-key reference. There is no persistence or expiration cleanup; validity timestamps are embedded in the `ManagedSecretKey`.

## Dependencies and Integration Points
The class depends on Java Cryptography Architecture `KeyGenerator`, `SecretKey`, and HDDS `ManagedSecretKey`/`SecretKeyClient`. It is used by `TestOzoneDelegationTokenSecretManager` for symmetric token signatures.

## Risks and Edge Cases
The implementation is not thread-safe and does not simulate key service failures except when spied in tests. It throws a runtime exception if `HmacSHA256` is unavailable, which is effectively impossible on supported JVMs.

## Test Signals
The class provides deterministic API behavior with real cryptographic keys, making token signature tests more meaningful than byte-array stubs.
