# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/container/ContainerReplicaNotFoundException.java

## Purpose
Specific `ContainerException` indicating a container replica is missing for a container/datanode pair.

## Important APIs, Types, And Functions
Constructors include no-arg, message-only for remote unwrap, and `ContainerID` plus `DatanodeDetails` for formatted messages. All result-bearing constructors use `CONTAINER_REPLICA_NOT_FOUND`.

## Control Flow
Thrown by replica lookup or mutation paths when expected replica metadata cannot be found.

## State And Persistence
Only inherited exception state is kept.

## Dependencies And Integration Points
Depends on `DatanodeDetails`, `ContainerID`, and `ContainerException`. Integrated by container manager and client error handling.

## Risks And Test Signals
No-arg constructor yields null message components through delegation. Tests should cover result code, formatted message, and remote unwrap constructor behavior.
