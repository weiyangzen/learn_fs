<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/transport/server/XceiverServerSpi.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/transport/server/XceiverServerSpi.java

## Purpose

`XceiverServerSpi` defines the common datanode container transport-server contract implemented by standalone gRPC and Ratis servers. The complete 96-line interface was read.

## Important APIs, Types, and Functions

Required methods are `start`, `stop`, `getIPCPort`, `getServerType`, `submitRequest`, `isExist`, and `getPipelineReport`. Default no-op or nullable extension points are `addGroup(pipelineId, peers)`, `addGroup(pipelineId, peers, priorityList)`, `removeGroup`, and `getStorageReport`.

## Control Flow

There is no implementation flow except default no-op methods. Concrete servers implement lifecycle, request submission, pipeline membership, and reporting.

## State and Persistence Behavior

The interface owns no state. Implementations may manage network sockets, Ratis groups, log directories, and container persistence through dispatchers.

## Dependencies and Integration Points

It exposes protocol types from HDDS/Ozone protobufs, `DatanodeDetails`, `ContainerCommandRequestProto`, `PipelineReport`, and metadata storage reports. It is used by higher-level datanode services without needing to know the replication transport.

## Risks and Edge Cases

Default `getStorageReport` returns null, so callers must tolerate missing metadata storage reports. Group-management defaults are no-op, which is correct for standalone but dangerous if a Ratis implementation forgets to override them.

## Test Signals

Contract tests should exercise both implementations through this SPI, especially submit failure semantics, pipeline existence/report behavior, and default method assumptions.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/transport/server/XceiverServerSpi.java -->
