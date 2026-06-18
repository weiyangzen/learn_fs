# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/RemoveSCMRequest.java

## Purpose
Models an HA request to remove an SCM from the SCM Ratis membership ring. It carries cluster ID, SCM ID, and the SCM Ratis address to remove.

## Important APIs, Types, And Functions
`RemoveSCMRequest` has constructor/getters and `getProtobuf()` producing `HddsProtos.RemoveScmRequestProto`.

## Control Flow
Callers construct a request and serialize it for RPC. Unlike `AddSCMRequest`, this file has no `getFromProtobuf` helper.

## State And Persistence
The object is immutable. Persistence is external to the HA removal service or Ratis membership log.

## Dependencies And Integration Points
Depends on `HddsProtos.RemoveScmRequestProto` and integrates with SCM HA administrative membership changes.

## Risks And Test Signals
Missing validation and missing parse helper can lead to asymmetry in call sites. Tests should cover protobuf creation and receiver-side validation for IDs/address and cluster mismatch.
