# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/token/TokenVerifier.java

## Purpose

`TokenVerifier` is the common interface for Ozone gRPC/container-token header validation. It provides direct token verification, encoded-token decoding, and a factory that selects no-op or composite block/container verification based on security configuration.

## Important APIs, Types, and Functions

`verify(Token<?> token, ContainerCommandRequestProtoOrBuilder cmd)` is the required method. The default `verify(cmd, encodedToken)` rejects null/empty values, decodes the URL-safe Hadoop token string, and delegates. Static `create(SecurityConfig, SecretKeyVerifierClient)` returns `NoopTokenVerifier` when both token types are disabled, otherwise a `CompositeTokenVerifier` containing `BlockTokenVerifier` and `ContainerTokenVerifier`.

## Control Flow

Callers can pass encoded metadata directly. The default method enforces that a token exists before decoding. The factory chooses verifier topology at service startup or translator construction time.

## State and Persistence Behavior

The interface owns no state. Implementations may hold configuration and secret-key clients; verification state is per request.

## Dependencies and Integration Points

It sits between container command handlers and the Ozone security token subsystem. It depends on Guava `Strings`, Hadoop `Token`, protobuf command builders, `SecurityConfig`, and `SecretKeyVerifierClient`.

## Risks and Edge Cases

Implementations that do not override the encoded-token overload will reject empty tokens. The factory always installs both block and container verifiers when either token type is enabled, relying on each verifier's `isTokenRequired` predicate to bypass irrelevant commands.

## Test Signals

Test empty/null encoded token rejection, invalid URL token decode, factory selection for all four block/container enablement combinations, and composite behavior where only the relevant verifier enforces a command.
