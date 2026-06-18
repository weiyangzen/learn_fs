# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/security/token/CompositeTokenVerifier.java

## Purpose
`CompositeTokenVerifier` runs multiple `TokenVerifier` delegates for a single datanode command.

## Important APIs, Types, And Functions
The constructor copies a provided delegate list into an internal `LinkedList`. `verify(Token<?>, ContainerCommandRequestProtoOrBuilder)` iterates over delegates and calls each verifier.

## Control Flow
Verification is sequential. The first delegate throwing `SCMSecurityException` aborts the chain; otherwise all verifiers must pass.

## State, Persistence, And Dependencies
State is the delegate list. There is no persistence. Dependencies are Hadoop tokens, datanode command protobufs, and SCM security exceptions.

## Integration Points
Container command handling can combine block token, container token, and other token verifiers without embedding knowledge of each verifier type.

## Risks
Delegate ordering matters for error surface and cost. The list is mutable internally but not exposed. Passing null delegates or null list is not guarded.

## Test Signals
Tests should verify all delegates are invoked on success, iteration stops on first failure, ordering, empty delegate behavior, and null input handling.
