# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/container/common/helpers/ContainerNotOpenException.java

## Purpose
Storage-container exception for operations requiring an open container when the target container is not open.

## Important APIs, Types, And Functions
Constructor maps the message to `ContainerProtos.Result.CONTAINER_NOT_OPEN`.

## Control Flow
Thrown by write/update paths when lifecycle state disallows mutation.

## State And Persistence
Only inherited exception fields.

## Dependencies And Integration Points
Depends on `StorageContainerException` and datanode protobuf result codes. Integrated by container state validation in datanode handlers.

## Risks And Test Signals
Tests should cover write attempts on closed/quasi-closed/deleting containers and verify wire result codes.
