# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/AddSCMRequest.java

## Purpose
Models an HA bootstrap request for adding an SCM node to an existing SCM Ratis ring. It carries the cluster ID, SCM ID, and Ratis address of the joining SCM.

## Important APIs, Types, And Functions
`AddSCMRequest` exposes constructor/getters, `getProtobuf()`, static `getFromProtobuf(HddsProtos.AddScmRequestProto)`, and nested `Builder` with setters for cluster ID, SCM ID, and Ratis address.

## Control Flow
Callers either build the object directly, through `Builder`, or from protobuf. `getProtobuf()` serializes all three fields into `AddScmRequestProto` for SCM-to-SCM RPC.

## State And Persistence
The instance is immutable after construction. Persistent behavior is limited to protobuf transport and any later storage done by the HA bootstrap path.

## Dependencies And Integration Points
Depends on `HddsProtos.AddScmRequestProto` and integrates with SCM HA bootstrap APIs and Ratis membership management.

## Risks And Test Signals
There is no validation for null/empty IDs or malformed addresses, so upstream validation must be covered. Tests should verify protobuf round trips and rejection behavior in the receiving SCM service.
