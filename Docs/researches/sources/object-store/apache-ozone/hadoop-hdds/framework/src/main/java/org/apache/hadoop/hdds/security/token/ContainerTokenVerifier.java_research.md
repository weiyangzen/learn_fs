# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/token/ContainerTokenVerifier.java

## Purpose

`ContainerTokenVerifier` adapts the generic short-lived token verifier to Ozone container tokens. It decides when datanode container commands require a token, creates the container-token identifier used for deserialization, and binds the token service check to the container ID in the protobuf command.

## Important APIs, Types, and Functions

The class extends `ShortLivedTokenVerifier<ContainerTokenIdentifier>`. Its constructor accepts `SecurityConfig` and `SecretKeyVerifierClient`. `isTokenRequired(ContainerProtos.Type)` combines `SecurityConfig.isContainerTokenEnabled()` with `HddsUtils.requireContainerToken(cmdType)`. `createTokenIdentifier()` returns a fresh `ContainerTokenIdentifier`. `getService(ContainerCommandRequestProtoOrBuilder)` converts `cmd.getContainerID()` to `ContainerID`.

## Control Flow

All verification flow is inherited. When `verify` is called, the base class asks this class whether the command type is protected, decodes the token identifier, validates the secret-key signature, checks expiration, compares the token service string with the command container ID, and then runs the no-op extension hook.

## State and Persistence Behavior

No mutable state is owned here beyond constructor-injected base-class fields. It depends on the external secret-key verifier client for current/older signing keys and on command contents for the service identity.

## Dependencies and Integration Points

It integrates datanode container RPC command validation with `HddsUtils.requireContainerToken`, `ContainerProtos`, `ContainerID`, `SecurityConfig`, and `SecretKeyVerifierClient`. It is normally installed through `TokenVerifier.create` alongside the block verifier.

## Risks and Edge Cases

The service comparison relies on `ContainerID.toString()` matching the token identifier service string. Misclassification in `HddsUtils.requireContainerToken` weakens enforcement for a command type. A missing or expired signing key causes rejection even if the token itself has not expired.

## Test Signals

Useful tests include enabled/disabled container-token configuration, commands that do and do not require tokens, container ID mismatch, expired token, missing secret key, invalid signature, and a valid token generated with the matching `ContainerTokenIdentifier` service.
