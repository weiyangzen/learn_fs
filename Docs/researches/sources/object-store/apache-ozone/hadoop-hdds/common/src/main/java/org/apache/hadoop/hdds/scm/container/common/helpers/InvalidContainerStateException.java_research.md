# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/container/common/helpers/InvalidContainerStateException.java

## Purpose
Storage-container exception for invalid lifecycle state transitions or operations.

## Important APIs, Types, And Functions
Constructor maps a message to `ContainerProtos.Result.INVALID_CONTAINER_STATE`.

## Control Flow
Thrown when container state validation fails before executing an operation or transition.

## State And Persistence
Only inherited exception state.

## Dependencies And Integration Points
Depends on `StorageContainerException` and datanode protobuf result codes. Integrated by container state machine and protocol handlers.

## Risks And Test Signals
Tests should cover invalid state transitions and verify result-code propagation over container protocol RPC.
