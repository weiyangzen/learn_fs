<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/transport/server/ratis/LocalStream.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/transport/server/ratis/LocalStream.java

## Purpose

`LocalStream` adapts a local `StateMachine.DataChannel` plus executor into a Ratis `StateMachine.DataStream` for datanode stream writes. The complete 55-line file was read.

## Important APIs, Types, and Functions

The package-private class implements `StateMachine.DataStream` with `getDataChannel()`, `cleanUp()`, and `getExecutor()`. Its constructor receives a data channel and executor.

## Control Flow

`cleanUp` requires the channel to be a `KeyValueStreamDataChannel`; otherwise it returns an exceptional future. For expected channels, it asynchronously calls `KeyValueStreamDataChannel.cleanUp()` on the provided executor.

## State and Persistence Behavior

The class only stores references. Actual stream data persistence and cleanup are owned by `KeyValueStreamDataChannel`.

## Dependencies and Integration Points

It is created by `ContainerStateMachine.stream` and later checked by `ContainerStateMachine.link`. It integrates with Ratis stream APIs and key-value container stream data channels.

## Risks and Edge Cases

A null or incompatible executor/channel will fail asynchronously or by class check. Cleanup assumes the executor remains alive through stream cleanup.

## Test Signals

Tests should cover successful cleanup for `KeyValueStreamDataChannel`, exceptional cleanup for unexpected channel types, executor usage, and link/cleanup lifecycle with `ContainerStateMachine`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/transport/server/ratis/LocalStream.java -->
