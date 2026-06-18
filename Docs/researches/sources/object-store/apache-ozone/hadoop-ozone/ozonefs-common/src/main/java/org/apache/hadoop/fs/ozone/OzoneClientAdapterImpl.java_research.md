<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs-common/src/main/java/org/apache/hadoop/fs/ozone/OzoneClientAdapterImpl.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozonefs-common/src/main/java/org/apache/hadoop/fs/ozone/OzoneClientAdapterImpl.java

## Purpose
Full-featured adapter implementation for bucket-scoped `o3fs://` filesystems that adds storage statistic accounting to `BasicOzoneClientAdapterImpl`.

## Important APIs, types, and functions
It provides constructors for default configuration, `OzoneConfiguration`, or explicit OM host/port plus volume and bucket. It overrides protected `incrementCounter` to update `OzoneFSStorageStatistics`.

## Control flow
All functional behavior is inherited from `BasicOzoneClientAdapterImpl`; this subclass only wires a statistics object and increments it when base adapter operations call the hook.

## State and persistence behavior
The local state is an optional `OzoneFSStorageStatistics` reference. Persistent Ozone state is managed by the inherited adapter.

## Dependencies and integration points
Created by Hadoop 3/main `OzoneFileSystem` so object-store operation counters and Hadoop storage statistics reflect adapter-level operations such as objects read, created, renamed, deleted, listed, and queried.

## Risks and test signals
Risk is low but important for observability: missing statistics wiring makes `StorageStatistics` under-report work. Tests should verify counters change for file create, read, list, delete, and rename through the full filesystem.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs-common/src/main/java/org/apache/hadoop/fs/ozone/OzoneClientAdapterImpl.java -->
