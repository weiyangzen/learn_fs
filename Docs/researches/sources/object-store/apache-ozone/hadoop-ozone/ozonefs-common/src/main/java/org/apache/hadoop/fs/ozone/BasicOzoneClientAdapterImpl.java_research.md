<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs-common/src/main/java/org/apache/hadoop/fs/ozone/BasicOzoneClientAdapterImpl.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozonefs-common/src/main/java/org/apache/hadoop/fs/ozone/BasicOzoneClientAdapterImpl.java

Purpose: bucket-scoped `OzoneClientAdapter` implementation for `BasicOzoneFileSystem`. It binds one volume and bucket, exposes Hadoop filesystem operations over Ozone client APIs, and intentionally omits statistics support.

Important APIs and functions: constructors for default/configured/host-port clients, `readFile`, `createFile`, `createStreamFile`, `renameKey`, `createDirectory`, `deleteObject(s)`, `getFileStatus`, `listKeys`, `listStatus`, delegation token and key provider methods, file checksum, snapshot create/rename/delete/diff, lease recovery, `finalizeBlock`, `setTimes`, `isFileClosed`, and `setSafeMode`.

Control flow: construction validates HA service-id/port combinations, creates an RPC `OzoneClient`, resolves volume/bucket, refreshes bucket replication config on a timer, validates link bucket layout, and closes the client if initialization fails. File IO delegates to `OzoneBucket`, translating common `OMException` result codes to Hadoop exceptions. Listing converts full or light Ozone statuses to `FileStatusAdapter`. Snapshot diff creates temporary snapshots when either side is the active filesystem, polls until jobs are `DONE`, aggregates paged reports, then deletes temporary snapshots.

State and persistence behavior: persistent mutations happen through Ozone OM/object-store calls: file creation, directory creation, deletes, renames, snapshots, lease recovery, block finalization, times, and safe mode. Local state caches client, object store, volume, bucket, replication configs, security flag, configured datanode port, config, and clock.

Dependencies and integration: Ozone client, OM helpers, HDDS replication/pipeline/container calls, Hadoop `FileStatus`/checksum/token abstractions, `OzoneTokenIdentifier`, and SLF4J. Risks include stale bucket replication config, exception swallowing in delete returning false, unsupported EC/non-replicated finalize fallback, blocking snapshot diff polling, and no-op counters. Test signals should cover exception translation, replication refresh, snapshot temp cleanup, block location host/port mapping, and lease recovery errors.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs-common/src/main/java/org/apache/hadoop/fs/ozone/BasicOzoneClientAdapterImpl.java -->
