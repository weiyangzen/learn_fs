# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/balancer/ContainerBalancerTaskIterationStatusInfo.java

Purpose: immutable status aggregate for one Container Balancer iteration, combining `IterationInfo`, `ContainerMoveInfo`, and `DataMoveInfo` into a public read model and protobuf export.

Important APIs: constructor, getters for iteration number/result/duration, scheduled and moved bytes, move counts, timeout counts, and entering/leaving node maps. `toProto()` builds `ContainerBalancerTaskIterationStatusInfoProto`; `mapToProtoNodeTransferInfo()` converts `Map<DatanodeID, Long>` into protobuf node transfer records using `DatanodeID.toString()` as UUID text.

Control flow and state: no persistence and no mutation after construction, but it exposes the underlying maps returned by `DataMoveInfo`. `toProto()` substitutes an empty string for a null iteration result, but assumes iteration duration and maps are non-null.

Dependencies and integration: consumed by balancer status APIs and tests in `TestContainerBalancerStatusInfo`; serialized through `StorageContainerLocationProtocolProtos` for SCM client responses.

Risks: null maps or duration can fail protobuf conversion; node UUID formatting depends on `DatanodeID.toString()`. Test signals should cover proto conversion, empty/null result text, and map ordering independence.
