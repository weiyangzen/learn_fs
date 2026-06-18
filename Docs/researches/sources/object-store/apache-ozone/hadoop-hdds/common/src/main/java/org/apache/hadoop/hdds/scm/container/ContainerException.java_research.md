# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/container/ContainerException.java

## Purpose
Base exception for ContainerManager failures, specializing `SCMException` with container-oriented result codes.

## Important APIs, Types, And Functions
Constructors accept a message alone for remote-exception unwrapping or a message plus `ResultCodes`.

## Control Flow
Callers throw this or subclasses when container operations fail; RPC layers can unwrap by constructor signature.

## State And Persistence
State is the inherited message/cause and `SCMException.ResultCodes`. No persistence.

## Dependencies And Integration Points
Depends on `SCMException` and integrates with container manager APIs, Hadoop RPC remote exception handling, and client error decoding.

## Risks And Test Signals
The message-only constructor sets a null result, so callers expecting result codes must handle null. Tests should cover subclass result propagation and remote exception unwrap behavior.
