# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/pipeline/InsufficientDatanodesException.java

## Purpose
`InsufficientDatanodesException` is an `IOException` indicating pipeline creation could not find enough datanodes.

## Important APIs, Types, And Functions
It stores `required` and `available` node counts. Constructors support remote-exception unwrapping by message only, explicit required/available/message, and default message formatting. Getters expose both counts.

## Control Flow
Placement or provider code can throw this exception when selected node count is below replication requirements. The message-only constructor sets counts to zero because remote unwrapping only supplies a message.

## State And Persistence Behavior
The exception carries transient required/available values and has no persistence.

## Dependencies And Integration Points
It extends `IOException` and is suitable for RPC propagation through Hadoop `RemoteException` unwrapping.

## Risks And Edge Cases
When reconstructed from a remote message, required and available are zero, so callers should not rely on counts unless they know the local constructor was used. Some placement code uses `SCMException` instead, so this exception is not the only insufficient-node signal.

## Test Signals
Tests should check message formatting, count getters, and remote-unwrapped constructor behavior.
