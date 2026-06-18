# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/container/common/helpers/BlockNotCommittedException.java

## Purpose
Storage-container exception for operations on blocks that are not committed.

## Important APIs, Types, And Functions
Constructor accepts a message and passes `ContainerProtos.Result.BLOCK_NOT_COMMITTED` to `StorageContainerException`.

## Control Flow
Thrown by container/block read or metadata paths when a block has not reached committed state.

## State And Persistence
Only inherited exception state is kept.

## Dependencies And Integration Points
Depends on datanode `ContainerProtos` result codes and `StorageContainerException`. Integrated by datanode container protocol error responses.

## Risks And Test Signals
Tests should assert result mapping and client translation for uncommitted block reads.
