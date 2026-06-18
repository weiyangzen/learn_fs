# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/token/NoopTokenVerifier.java

## Purpose

`NoopTokenVerifier` is the permissive `TokenVerifier` implementation used when block and container token enforcement are disabled. It preserves the verifier interface without requiring callers to branch around verification.

## Important APIs, Types, and Functions

It implements both `verify(Token<?> token, ContainerCommandRequestProtoOrBuilder cmd)` and `verify(ContainerCommandRequestProtoOrBuilder cmd, String encodedToken)`. Both methods intentionally return without inspecting token, encoded token, or command.

## Control Flow

There is no internal control flow. The explicit encoded-token overload bypasses the default interface method, preventing an empty-token failure in deployments where security settings intentionally disable token checks.

## State and Persistence Behavior

The class is stateless and has no persistence behavior.

## Dependencies and Integration Points

It is selected by `TokenVerifier.create` when both `SecurityConfig.isBlockTokenEnabled()` and `SecurityConfig.isContainerTokenEnabled()` are false. It is used by container RPC paths that always call a verifier even in insecure or token-disabled deployments.

## Risks and Edge Cases

Accidental selection due to incorrect configuration disables token authorization completely. Tests should verify it is only created when both block and container token flags are false.

## Test Signals

Check that null/empty encoded tokens do not fail under this verifier, that normal `TokenVerifier.create` returns it only for fully disabled token settings, and that callers still execute successfully through the shared verifier call path.
