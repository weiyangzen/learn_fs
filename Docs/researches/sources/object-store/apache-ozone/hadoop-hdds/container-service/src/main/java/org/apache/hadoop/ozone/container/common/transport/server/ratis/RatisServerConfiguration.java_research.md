<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/transport/server/ratis/RatisServerConfiguration.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/transport/server/ratis/RatisServerConfiguration.java

## Purpose

`RatisServerConfiguration` exposes configuration binding for Ratis server snapshot retention. The complete 47-line file was read.

## Important APIs, Types, and Functions

The class is annotated `@ConfigGroup(prefix = "hdds.ratis.server")`. It defines `numSnapshotsRetained` with `@Config(key = "hdds.ratis.server.num.snapshots.retained", type = INT, defaultValue = "5", tags = STORAGE)`, plus getter and setter.

## Control Flow

There is no complex flow. Ozone configuration binding populates the field, and `XceiverServerRatis.newRaftProperties()` reads it to set `RaftServerConfigKeys.Snapshot.setRetentionFileNum`.

## State and Persistence Behavior

The class holds in-memory configuration only. Snapshot files retained or deleted are controlled by Ratis using this value.

## Dependencies and Integration Points

It depends on HDDS config annotations and integrates with `XceiverServerRatis`.

## Risks and Edge Cases

Invalid or low values could remove diagnostic snapshots earlier than expected. Because the key repeats the group prefix in the annotation, config binding behavior should be verified against existing HDDS config conventions.

## Test Signals

Tests should verify default binding to 5, custom value binding, and propagation into Ratis snapshot retention properties.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/transport/server/ratis/RatisServerConfiguration.java -->
