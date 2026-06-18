<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/SnapshotInfo.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/SnapshotInfo.java

## Purpose

`SnapshotInfo` is the persisted metadata model for a bucket snapshot. It stores snapshot UUID, volume/bucket/name, status, creation/deletion time, previous snapshot links, checkpoint path, cleanup flags, size accounting, and transaction markers.

## Important APIs, Types, And Functions

Important methods include `getCodec`, setters/getters, `toBuilder`, nested `Builder`, `getProtobuf`, `builderFromProtobuf`, `getFromProtobuf`, `toAuditMap`, `getCheckpointDirName`, `getTableKey`, `generateName`, `newInstance`, `copyObject`, and `SnapshotStatus` enum conversions.

## Control Flow, State, And Persistence

The delegated codec persists `SnapshotInfo` through `OzoneManagerProtocolProtos.SnapshotInfo`. `newInstance` creates default active snapshots with generated names when needed, invalid deletion time, initial previous-snapshot IDs, and bucket snapshot path. Serialization conditionally includes optional previous IDs and transaction info while writing cleanup/size fields.

## Dependencies And Integration Points

It depends on HDDS UUID protobuf helpers, DB codecs, `ByteString`, Ozone constants, auditing, and snapshot protobufs. It integrates with OM snapshot tables, checkpoint directory naming, snapshot cleanup/deep-clean services, snapshot diff, audit logging, and list/get snapshot APIs.

## Risks And Test Signals

`INITIAL_SNAPSHOT_ID` is randomly generated at class load, so tests should verify intended sentinel behavior across process restarts if persisted. Equality omits the two delta size fields while `toString` includes them. Tests should cover protobuf round trips for optional fields, generated UTC names, table keys, checkpoint versions, status enum conversion, size accounting, cleanup flags, and copy isolation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/SnapshotInfo.java -->
