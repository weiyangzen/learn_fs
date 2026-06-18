# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/security/S3SecretStoreMap.java

## Purpose
`S3SecretStoreMap` is a simple in-memory test implementation of `S3SecretStore` backed by a concurrent map.

## Important APIs, Types, and Functions
- Constructor copies an initial `Map<String, S3SecretValue>`.
- `storeSecret` inserts or replaces a secret by Kerberos ID.
- `getSecret` returns the stored `S3SecretValue` or null.
- `revokeSecret` removes a secret.
- `batcher()` returns null because batch semantics are not needed in these tests.

## Control Flow
The implementation is direct map delegation with no validation or transformation. It is used by S3 authentication tests through `S3SecretManagerImpl` and locking wrappers.

## State and Persistence Behavior
State is held in a `ConcurrentHashMap` for test-thread safety. There is no persistence, batching, or transactional behavior.

## Dependencies and Integration Points
It implements `org.apache.hadoop.ozone.om.S3SecretStore` and stores `S3SecretValue` objects. It integrates with `S3SecretManagerImpl`, `S3SecretLockedManager`, and `OzoneDelegationTokenSecretManager` S3 auth validation tests.

## Risks and Edge Cases
Returning null from `batcher()` is acceptable for current tests but would be unsafe for code paths expecting batch operations. The store does not simulate persistence failures, serialization, or lock contention.

## Test Signals
The class is a lightweight fixture signal: S3 auth tests can focus on signature validation and token behavior without requiring a real OM metadata-backed secret store.
