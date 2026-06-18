<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs-common/src/main/java/org/apache/hadoop/fs/ozone/OzoneClientAdapter.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozonefs-common/src/main/java/org/apache/hadoop/fs/ozone/OzoneClientAdapter.java

## Purpose
Narrow adapter interface between Hadoop filesystem classes and Ozone client/OM APIs. It stabilizes the signatures shared across Hadoop compatibility modules and classloaders.

## Important APIs, types, and functions
The interface covers lifecycle, read/create stream operations, rename, directory create, single and batched deletes, key iteration, status listing, delegation tokens, server defaults, encryption key providers, canonical service name, replication, checksums, snapshots, snapshot diffs, lease recovery, block finalization, timestamps, file-closed checks, and safe mode.

## Control flow
Implementations translate Hadoop-oriented path strings and metadata requests into Ozone object store, volume, bucket, key, and OM protocol operations. Filesystem classes treat this interface as the only mutation/query surface.

## State and persistence behavior
The interface itself has no state. Its methods drive all persistent Ozone filesystem mutations: key data, directory markers, metadata, snapshots, recovery commits, and safe mode transitions.

## Dependencies and integration points
It references only the necessary Hadoop and Ozone types: streams, `FileStatusAdapter`, `BasicKeyInfo`, tokens, `OzoneFsServerDefaults`, `LeaseKeyInfo`, `OmKeyArgs`, `OmKeyLocationInfo`, and `SnapshotDiffReport`. Implementations in this subset add storage statistic forwarding.

## Risks and test signals
Because all filesystem behavior funnels through this API, signature changes have cross-module impact. Tests should verify adapter implementations preserve semantics for recursive operations, snapshot paths, token renewal, lease recovery, and capability-dependent stream creation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs-common/src/main/java/org/apache/hadoop/fs/ozone/OzoneClientAdapter.java -->
