# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/token/ContainerTokenIdentifier.java

## Purpose
`ContainerTokenIdentifier` is the short-lived token identifier for container-scoped operations.

## Important APIs, Types, And Functions
It extends `ShortLivedTokenIdentifier`, defines kind `HDDS_CONTAINER_TOKEN`, stores a `ContainerID`, and provides constructors with owner/container/expiry and optional secret-key UUID. Serialization uses `ContainerTokenSecretProto` in `getBytes()`, `write()`, `readFields()`, and `readFromByteArray()`. `getService()` returns the container id string.

## Control Flow
Serialization writes the protobuf bytes containing owner, secret-key id, expiry millis, and container id. Deserialization parses the protobuf and restores those fields. Equality delegates to the superclass and compares `containerID` with `==`.

## State, Persistence, And Dependencies
State is inherited owner/expiry/secret key id plus container id. Persistence is token byte serialization. Dependencies include protobuf container-token secret messages, Ozone protobuf UUID utilities, Hadoop `Text`, and `ContainerID`.

## Integration Points
`ContainerTokenSecretManager` creates these identifiers. Short-lived token verifiers read them to validate container token service, expiry, and signature.

## Risks
`equals()` uses reference equality for `ContainerID`, which may be wrong if equal IDs are distinct objects. `hashCode()` includes expiry but not container id directly, which may be inconsistent with equality intent. `readFields()` requires `DataInputStream` with mark support and casts `DataInput`.

## Test Signals
Tests should cover protobuf round trip, token kind/service, equality/hash behavior for equivalent container IDs, readFields input assumptions, and secret-key id preservation.
