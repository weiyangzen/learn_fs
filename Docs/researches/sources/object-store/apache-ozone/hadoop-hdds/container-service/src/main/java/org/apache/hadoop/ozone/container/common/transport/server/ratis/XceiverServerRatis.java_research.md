<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/transport/server/ratis/XceiverServerRatis.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/transport/server/ratis/XceiverServerRatis.java

## Purpose

`XceiverServerRatis` is the datanode container transport server for RATIS replication. It owns the local `RaftServer`, creates `ContainerStateMachine` instances per pipeline, manages Ratis ports and properties, accepts local command submissions, tracks active pipelines, and reports or closes pipelines on Ratis failure signals. The complete 992-line file was read.

## Important APIs, Types, and Functions

Primary APIs include `newXceiverServerRatis`, `start`, `stop`, `submitRequest`, `addGroup`, `removeGroup`, `isExist`, `getPipelineReport`, `getMinReplicatedIndex`, `getRaftPeersInPipeline`, and notification handlers invoked by `ContainerStateMachine`. Configuration helpers include `newRaftProperties`, `assignPorts`, `setUpRatisStream`, `setStateMachineDataConfigurations`, `setRaftSegmentAndWriteBufferSize`, `setPendingRequestsLimits`, and TLS parameter creation. `ActivePipelineContext` tracks whether this datanode is leader and whether a close action is pending.

## Control Flow

Construction assigns client/admin/server ports, optionally using separate Ratis ports depending on datanode version, enables data stream if configured, creates chunk executors, builds Ratis properties, and constructs a recover-mode `RaftServer` with a state-machine registry. `start` prestarts chunk writer threads, starts Ratis, and records actual bound ports back into `DatanodeDetails`, including datastream port when enabled. `submitRequest` wraps a container command as a `RaftClientRequest`, submits it to the local server with a timeout, and raises not-leader or state-machine exceptions. `addGroup` builds a Ratis group from pipeline peers and priority list; `removeGroup` removes it while either deleting or preserving logs. Failure handlers translate slowness, no leader, apply failure, log failure, and snapshot-install notifications into SCM pipeline close actions and immediate heartbeat triggers.

## State and Persistence Behavior

Persistent state is primarily Ratis log/snapshot storage under configured datanode Ratis directories. `shouldDeleteRatisLogDirectory` controls whether removed group logs are deleted or renamed/preserved. Runtime state includes port fields, `activePipelines`, chunk executor pools, a generated Ratis client id, and request call id counter.

## Dependencies and Integration Points

The class integrates with Apache Ratis server/group-management APIs, Ozone config keys, `DatanodeRatisServerConfig`, `RatisHelper`, `ContainerDispatcher`, `ContainerController`, `StateContext`, tracing, TLS certificate clients, and SCM pipeline actions/reports.

## Risks and Edge Cases

Misconfigured log appender byte limits larger than segment size are rejected by assertion. Pipeline-close triggering assumes `activePipelines.get(groupId)` is present when context exists. Snapshot installation is intentionally treated as fatal to the pipeline because snapshots do not contain enough data for catch-up. `submitRequest` is local and times out by config, so callers must handle `IOException` wrapping timeout or execution failures. TLS parameters are null when security/TLS is disabled.

## Test Signals

Tests should cover fixed/random/separate port assignment, Ratis property generation for log sizes, state-machine data caching, snapshot retention and data stream options, TLS parameter creation, add/remove group behavior and log-retention flags, submitRequest reply exception mapping, pipeline report leader flag updates, immediate heartbeat on pipeline close, and failure notification paths.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/transport/server/ratis/XceiverServerRatis.java -->
