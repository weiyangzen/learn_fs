# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/balancer/DataMoveInfo.java

Purpose: value object for balancer data movement volume: scheduled bytes, actually moved bytes, bytes entering target nodes, and bytes leaving source nodes.

Important APIs: constructor and getters for `sizeScheduledForMove`, `dataSizeMoved`, `sizeEnteringNodes`, and `sizeLeavingNodes`.

Control flow and state: construction records references, not defensive copies. The object is otherwise immutable by field assignment but map contents may still be externally mutable.

Dependencies and integration: built from source and target strategy accounting maps, then included in `ContainerBalancerTaskIterationStatusInfo` and converted to protobuf status.

Risks: exposed mutable maps can drift after status construction if callers reuse strategy maps; no validation for negative byte totals. Tests should verify status snapshots do not accidentally change across balancer iteration reset, or callers should pass copies before construction.
