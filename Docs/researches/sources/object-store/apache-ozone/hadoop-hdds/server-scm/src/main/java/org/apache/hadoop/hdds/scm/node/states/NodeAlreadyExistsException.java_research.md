# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/node/states/NodeAlreadyExistsException.java

## Purpose
`NodeAlreadyExistsException` signals that a datanode with the same `DatanodeID` already exists in `NodeStateMap`.

## Important APIs, Types, And Functions
It extends `NodeException` and provides a no-argument constructor plus a `DatanodeID` constructor that formats a useful message.

## Control Flow
`NodeStateMap.addNode` throws it when the ID key is already present. Callers such as `SCMNodeManager.register` catch it as a benign duplicate-registration path.

## State And Persistence Behavior
The exception carries only a message. It has no persistent behavior.

## Dependencies And Integration Points
It depends on `DatanodeID` and the node state map exception hierarchy. It is part of the checked-exception contract for node insertion.

## Risks And Edge Cases
The no-argument constructor yields a null message, which is less useful in logs. Duplicate registration may be benign or a symptom depending on caller context, so catch sites should preserve enough context.

## Test Signals
Tests should verify duplicate add throws this type and message-bearing construction includes the datanode ID.
