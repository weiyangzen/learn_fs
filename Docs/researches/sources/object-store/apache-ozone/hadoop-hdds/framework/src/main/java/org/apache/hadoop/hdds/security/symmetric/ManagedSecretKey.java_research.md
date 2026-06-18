# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/symmetric/ManagedSecretKey.java

## Purpose
`ManagedSecretKey` wraps a symmetric `SecretKey` with UUID, creation time, expiry time, signing/verification helpers, and protobuf serialization.

## Important APIs, Types, And Functions
Getters expose id, key, creation, and expiry. `isExpired()` compares expiry to now. `sign(byte[])` and `sign(TokenIdentifier)` compute HMAC via `Mac`. `isValidSignature(...)` compares expected and provided signatures with `MessageDigest.isEqual()`. `toProtobuf()` and `fromProtobuf()` convert to generated `ManagedSecretKey` messages.

## Control Flow
`getMac()` caches one `Mac` instance per thread id in a concurrent map, then each signing call initializes that `Mac` with the secret key and signs the data. Equality and hash code are based only on UUID.

## State, Persistence, And Dependencies
State is immutable key metadata and key material plus a per-thread `Mac` cache. Persistence is via protobuf or `LocalSecretKeyStore` DTOs. Dependencies include Java crypto, UUID/time APIs, protobuf byte strings, and Ozone protobuf utilities.

## Integration Points
`SecretKeyManager` generates these keys; signer/verifier clients distribute and cache them; short-lived token managers/verifiers use signing and verification.

## Risks
The raw `ConcurrentHashMap` uses no generic value type in construction. Per-thread `Mac` cache can grow with many transient threads. Equality by UUID ignores key material differences for the same id. Encoded key bytes are serialized over protobuf and local JSON.

## Test Signals
Tests should cover signing/verification, constant-time mismatch path, expiry, protobuf round trip, equality semantics, concurrent signing, and invalid algorithm behavior.
