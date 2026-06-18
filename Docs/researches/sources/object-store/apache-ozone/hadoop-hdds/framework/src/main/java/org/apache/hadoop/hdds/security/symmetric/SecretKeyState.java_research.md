# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/symmetric/SecretKeyState.java

## Purpose
`SecretKeyState` defines the replicated state holder contract for SCM-managed symmetric keys.

## Important APIs, Types, And Functions
It extends `SCMHandler`, exposes `getCurrentKey()`, `getKey(UUID)`, `getSortedKeys()`, replicated `updateKeys(List<ManagedSecretKey>)`, and `reinitialize(List<ManagedSecretKey>)`. `getType()` returns `SCMRatisProtocol.RequestType.SECRET_KEY`.

## Control Flow
The interface itself has no implementation. The `@Replicate` annotation on `updateKeys()` instructs SCM HA machinery to replicate key updates.

## State, Persistence, And Dependencies
State is implementation-defined. Dependencies include managed keys, SCM HA handler/replication annotations, and SCM exceptions.

## Integration Points
`SecretKeyManager` updates this state during initialization and rotation. SCM Ratis dispatch uses `getType()` to route replicated secret-key requests.

## Risks
Implementations must keep current, sorted, and id-indexed views consistent and durable. Replication failures surface as `SCMException`.

## Test Signals
Tests should verify replication annotation handling, request type, current key semantics, key lookup, sorted order, and snapshot reinitialization.
