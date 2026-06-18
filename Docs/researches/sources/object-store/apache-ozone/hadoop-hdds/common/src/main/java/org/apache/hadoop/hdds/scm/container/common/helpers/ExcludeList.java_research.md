# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/container/common/helpers/ExcludeList.java

## Purpose
Tracks datanodes, container IDs, and pipeline IDs a client wants SCM to avoid during allocation, optionally with automatic datanode expiry.

## Important APIs, Types, And Functions
APIs include `addDatanode(s)`, `addConatinerId` (misspelled but public), `addPipeline`, getters, `getProtoBuf`, `getFromProtoBuf`, `isEmpty`, `clear`, and `getExpiryTime`. Datanodes are held in a concurrent map to expiry timestamps; containers/pipelines are sets.

## Control Flow
Clients add failed or unsuitable targets. `getDatanodes()` prunes expired entries before returning. Protobuf conversion serializes container IDs, datanode UUID strings, and pipeline IDs.

## State And Persistence
State is mutable and transient per allocation/retry flow. Protobuf transport can carry it between client and SCM.

## Dependencies And Integration Points
Depends on `DatanodeDetails`, `ContainerID`, `PipelineID`, and HddsProtos. Integrated by SCM block allocation and retry logic.

## Risks And Test Signals
Container/pipeline sets are not concurrent, and protobuf deserialization reuses a datanode builder. The misspelled method is API surface. Tests should cover expiry pruning, protobuf round trip, empty/clear, and concurrent datanode access.
