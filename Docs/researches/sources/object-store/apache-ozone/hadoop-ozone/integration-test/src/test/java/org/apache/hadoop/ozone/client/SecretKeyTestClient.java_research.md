# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/client/SecretKeyTestClient.java

## Purpose
`SecretKeyTestClient` is a small test implementation of `SecretKeyClient` used to model OM secret-key rotation for delegation-token tests. It generates HMAC secret keys, exposes the current key, retains older keys by UUID, and lets tests rotate to a new current key while old keys remain retrievable.

## Important APIs, Types, and Functions
- Implements `SecretKeyClient.getCurrentSecretKey()` and `SecretKeyClient.getSecretKey(UUID)`.
- `rotate()` creates a new `ManagedSecretKey` and stores it in `keysMap`.
- `generateKey()` uses `KeyGenerator.getInstance("HmacSHA256")`, `UUID.randomUUID()`, `Instant.now()`, and `Instant.now().plus(Duration.ofHours(1))`.
- `ManagedSecretKey` carries key id, creation time, expiry time, and the generated `SecretKey`.

## Control Flow
The constructor immediately calls `rotate`, so a usable current key exists after construction. Each later `rotate` replaces `current` with a newly generated one and inserts it into the map. Lookup by ID returns either the matching current or older key, if it has been generated in this client instance.

## State and Persistence Behavior
State is in-memory only. There is no expiry enforcement or removal of old keys; the one-hour expiry timestamp is metadata consumed by downstream code. Because older keys remain in `keysMap`, tests can validate renewal of tokens signed by a previous key after rotation.

## Dependencies and Integration Points
The class is used by secure OM tests that inject a custom secret-key client into `OzoneManager`. It integrates with HDDS symmetric-key abstractions and Java cryptography but has no Ozone service dependencies of its own.

## Risks and Edge Cases
The implementation is intentionally minimal and not thread-safe. It does not simulate key deletion, expiry rejection, persistence, or failed key generation beyond wrapping the impossible missing `HmacSHA256` algorithm in `RuntimeException`. Tests using it should not infer production rotation cleanup behavior.

## Test Signals
Useful signals are distinct UUIDs after rotation, stable retrieval of old keys by ID, and token identifiers reflecting the current key id at creation time while old tokens can still be validated with retained keys.
