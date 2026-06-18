# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/impl/TestStorageLocationReport.java

## Purpose
`TestStorageLocationReport` verifies that `StorageLocationReport` serializes filesystem-level capacity fields into `StorageReportProto` and can reconstruct them from protobuf.

## Important APIs, Types, And Functions
- `StorageLocationReport.newBuilder()` sets ID, path, `StorageType`, capacity, SCM used bytes, remaining bytes, committed bytes, free-space-to-spare, reserved bytes, filesystem capacity, and filesystem available bytes.
- `getProtoBufMessage()` emits `StorageReportProto`.
- `StorageLocationReport.getFromProtobuf` parses protobuf back into a report object.

## Control Flow
The test builds a report with both logical storage accounting and filesystem capacity/available values. It asserts the proto has `fsCapacity` and `fsAvailable` populated, then parses it and verifies all expected numeric fields survived the round trip.

## State And Persistence Behavior
There is no persistent state. The behavior under test is a serialization contract between the datanode's local volume report model and SCM heartbeat protobufs.

## Dependencies And Integration Points
The file depends on Hadoop `StorageType`, HDDS `StorageReportProto`, and the local `StorageLocationReport` builder/parser. It integrates with heartbeat storage reporting because these proto fields are consumed by SCM.

## Risks And Edge Cases
The covered risk is silent loss of filesystem capacity/available fields when converting to/from protobuf. It does not cover unset optional fields, negative values, or builder validation.

## Test Signals
The signal is narrow but precise: it proves new filesystem fields are included in protobuf and parsed back alongside existing capacity, used, remaining, reserved, and spare-space fields.
