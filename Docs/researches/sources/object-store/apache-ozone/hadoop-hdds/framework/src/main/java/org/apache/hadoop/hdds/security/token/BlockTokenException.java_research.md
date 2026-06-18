# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/token/BlockTokenException.java

## Purpose
`BlockTokenException` is the block-token-specific exception type in the SCM security layer.

## Important APIs, Types, And Functions
It extends `SCMSecurityException` and provides constructors for message-only, message-plus-cause, and cause-only cases.

## Control Flow
There is no custom flow; constructors delegate to the superclass.

## State, Persistence, And Dependencies
No state beyond inherited exception fields. No persistence. Dependency is `SCMSecurityException`.

## Integration Points
`BlockTokenVerifier` throws this exception when a token lacks required permission for a datanode block command.

## Risks
The exception carries no specialized error code in these constructors, so callers rely on type/message unless the superclass supplies defaults.

## Test Signals
Tests should verify constructor message/cause propagation and handling by token verification call paths.
