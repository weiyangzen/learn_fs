# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/token/ContainerTokenGenerator.java

## Purpose
`ContainerTokenGenerator` defines how SCM/container code creates tokens authorizing operations on a container.

## Important APIs, Types, And Functions
`generateEncodedToken(ContainerID)` creates a URL-encoded token for the current user. `generateToken(String, ContainerID)` creates a Hadoop token for an explicit user. The `DISABLED` implementation returns an empty encoded string and an empty `Token`.

## Control Flow
The interface has no implementation flow except the disabled singleton's no-op behavior.

## State, Persistence, And Dependencies
No state in the interface; disabled singleton is stateless. Dependencies are `ContainerID` and Hadoop `Token`.

## Integration Points
`ContainerTokenSecretManager` implements this interface for enabled token generation. `StorageContainerLocationProtocol.getContainerToken()` exposes token acquisition over SCM RPC.

## Risks
Callers must handle disabled mode's empty token values. `generateEncodedToken()` may throw unchecked IO wrappers by contract.

## Test Signals
Tests should verify disabled behavior, enabled token generation via `ContainerTokenSecretManager`, URL encoding, and current-user lookup failure handling.
