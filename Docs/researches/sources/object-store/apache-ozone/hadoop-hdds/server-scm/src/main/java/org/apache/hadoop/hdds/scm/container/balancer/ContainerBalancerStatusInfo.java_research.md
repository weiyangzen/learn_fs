<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/balancer/ContainerBalancerStatusInfo.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/balancer/ContainerBalancerStatusInfo.java

## Purpose
Simple status DTO for exposing container balancer runtime status through protocol APIs.

## Important APIs, Types, And Functions
The class stores `startedAt`, a `ContainerBalancerConfigurationProto`, and a list of `ContainerBalancerTaskIterationStatusInfo`. Getters expose each field. `toProto` converts to `StorageContainerLocationProtocolProtos.ContainerBalancerStatusInfoProto`, encoding `startedAt` as epoch seconds and mapping iteration status objects through `toProto`.

## Control Flow
`ContainerBalancer.getBalancerStatusInfo` creates this object while the balancer is running. Protocol code calls `toProto` to serialize it for clients.

## State And Persistence
It is immutable runtime DTO state and has no persistence. The configuration embedded in it is a snapshot supplied by the balancer.

## Dependencies And Integration Points
Depends on protobuf types from `HddsProtos` and `StorageContainerLocationProtocolProtos`, Java time, and iteration status DTOs. It is the bridge from internal balancer task status to external SCM client protocol status.

## Risks And Test Signals
Epoch-second precision drops subsecond detail and omits timezone representation beyond the instant. Null inputs are not guarded. Tests should cover proto conversion, empty and non-empty iteration lists, started-at epoch value, and configuration passthrough.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/balancer/ContainerBalancerStatusInfo.java -->
