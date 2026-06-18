<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs-common/src/main/java/org/apache/hadoop/fs/ozone/RootedOzoneClientAdapterImpl.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozonefs-common/src/main/java/org/apache/hadoop/fs/ozone/RootedOzoneClientAdapterImpl.java

## Purpose
Full-featured adapter implementation for rooted `ofs://` filesystems that adds storage statistics to `BasicRootedOzoneClientAdapterImpl`.

## Important APIs, types, and functions
Constructors support default configuration, explicit `OzoneConfiguration`, or OM host/port plus `ConfigurationSource`. The override of `incrementCounter` forwards counts to optional `OzoneFSStorageStatistics`.

## Control flow
All filesystem operations are inherited. This subclass only wires statistics so inherited adapter code can report object-level activity.

## State and persistence behavior
Local state is an optional statistics reference. Durable Ozone state changes happen in inherited adapter methods.

## Dependencies and integration points
Created by full Hadoop 3/main `RootedOzoneFileSystem`. It integrates rooted OFS adapter operations with Hadoop storage statistics.

## Risks and test signals
Behavioral risk is limited to observability and constructor selection. Tests should verify rooted filesystem operations increment expected object counters and that null statistics remains safe.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs-common/src/main/java/org/apache/hadoop/fs/ozone/RootedOzoneClientAdapterImpl.java -->
