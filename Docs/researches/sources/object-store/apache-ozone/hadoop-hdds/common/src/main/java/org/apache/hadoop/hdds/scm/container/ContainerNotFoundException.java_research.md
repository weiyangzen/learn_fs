# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/container/ContainerNotFoundException.java

## Purpose
Specific `ContainerException` indicating that a requested container is absent from ContainerManager.

## Important APIs, Types, And Functions
Constructors support unknown ID, explicit message for remote unwrap, and `ContainerID`-formatted message. `newInstanceForTesting()` provides a fixed test exception.

## Control Flow
Thrown by lookup paths when container metadata is missing. Clients inspect `ResultCodes.CONTAINER_NOT_FOUND`.

## State And Persistence
No persistent state beyond inherited exception fields.

## Dependencies And Integration Points
Depends on `ContainerID` and `ContainerException`. Integrated by SCM RPC error mapping and tests.

## Risks And Test Signals
Default message is generic; tests should assert result code and message formats for lookup failures and remote unwrapping.
