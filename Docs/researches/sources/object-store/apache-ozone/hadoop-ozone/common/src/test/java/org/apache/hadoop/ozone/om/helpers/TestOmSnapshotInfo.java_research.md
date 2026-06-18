# sources/object-store/apache-ozone/hadoop-ozone/common/src/test/java/org/apache/hadoop/ozone/om/helpers/TestOmSnapshotInfo.java

Purpose: tests `SnapshotInfo` metadata conversion to/from protobuf, snapshot status mapping, size accounting fields, cleaning flags, and generated snapshot names.

Important APIs/types/functions: exercises `SnapshotInfo.Builder`, `getProtobuf`, `getFromProtobuf`, `SnapshotStatus.valueOf`, getters for IDs/names/status/sizes/flags, and `SnapshotInfo.generateName`.

Control flow and state: helper methods build equivalent object and protobuf records containing snapshot UUIDs, volume/bucket/name, previous snapshot IDs, path, deep-clean flags, referenced/exclusive sizes, replicated sizes, and deltas from directory deep cleaning. Tests compare individual fields and full object equality.

Dependencies and integration points: uses OM protobuf `SnapshotInfo`, `SnapshotStatusProto`, HDDS UUID protobuf conversion, and `Time`. The object is persisted by OM snapshot tables and used by snapshot diff/cleanup paths.

Risks and test signals: catches lost accounting fields, status mapping regressions, and protobuf/object equality drift. `generateName` asserts stable UTC-like timestamp formatting with millisecond precision for snapshot names.
