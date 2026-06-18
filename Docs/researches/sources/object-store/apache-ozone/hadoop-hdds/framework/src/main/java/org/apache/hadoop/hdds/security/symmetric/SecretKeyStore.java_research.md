# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/symmetric/SecretKeyStore.java

## Purpose
`SecretKeyStore` abstracts persistence for managed symmetric secret keys.

## Important APIs, Types, And Functions
It declares `load()` to return persisted managed keys and `save(Collection<ManagedSecretKey>)` to persist a key collection.

## Control Flow
There is no implementation control flow. `LocalSecretKeyStore` provides the local JSON-backed implementation.

## State, Persistence, And Dependencies
The interface has no state. Implementations define persistence medium and durability behavior.

## Integration Points
`SecretKeyManager` loads from a store during initialization. `SecretKeyStateImpl` saves to a store after key updates and reinitialization.

## Risks
The contract does not specify atomicity, ordering, encryption, or whether expired keys should be returned; callers perform filtering/sorting as needed.

## Test Signals
Implementation tests should verify round-trip persistence, failure handling, empty store behavior, and durability guarantees.
