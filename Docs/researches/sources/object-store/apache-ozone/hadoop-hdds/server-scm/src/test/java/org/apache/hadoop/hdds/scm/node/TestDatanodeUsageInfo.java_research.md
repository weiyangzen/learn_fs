# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/node/TestDatanodeUsageInfo.java

Purpose: verifies `DatanodeUsageInfo.toProto()` includes optional filesystem-level capacity fields only when they have been explicitly set.

Important APIs and types: creates random `DatanodeDetails`, `SCMNodeStat`, `DatanodeUsageInfo`, and converts to `HddsProtos.DatanodeUsageInfoProto` with `ClientVersion.CURRENT_VERSION`.

Control flow: `testToProtoDoesNotIncludeFilesystemFieldsByDefault()` asserts `hasFsCapacity()` and `hasFsAvailable()` are false while standard capacity/used/remaining are populated. `testToProtoIncludesFilesystemFieldsWhenPresent()` calls `setFilesystemUsage(2000L, 1500L)` and asserts the optional proto fields are present and correct.

State and persistence: no persistence. State is local object fields and generated protobufs.

Integration points and risks: protects client-facing or admin-facing datanode usage serialization, especially backward-compatible optional fields. It does not test older client versions, reserved/committed fields, sorting, or null datanode behavior.
