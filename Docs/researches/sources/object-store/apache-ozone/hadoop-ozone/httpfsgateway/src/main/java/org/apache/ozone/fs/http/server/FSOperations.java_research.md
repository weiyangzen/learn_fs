# sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/java/org/apache/ozone/fs/http/server/FSOperations.java

## Purpose
`FSOperations` is the execution library behind `HttpFSServer`. It converts WebHDFS-style REST operations into `FileSystemAccess.FileSystemExecutor` objects, performs Hadoop `FileSystem` calls, serializes results into JSON-friendly maps/objects/strings, and updates selected HttpFS metrics.

## Important APIs, Types, and Functions
Static helpers include `setBufferSize(Configuration)`, file status serializers, ACL/checksum/xattr/content-summary/quota/storage-policy serializers, `toJSON()`, and `copyBytes()`. Nested executors cover append, concat, truncate, content summary, quota usage, create, delete, checksum, file status, home dir, list status, batched listing, mkdirs, open, rename, owner/permission/time/replication updates, ACL operations, xattrs, storage policies, snapshots, server defaults, access checks, and erasure coding policy operations.

## Control Flow
`HttpFSServer` constructs an executor with parsed parameters and invokes it through `FileSystemAccess`. Each executor stores request parameters as `Path`, primitive values, parsed ACLs, or enum sets, then its `execute(FileSystem)` method makes exactly the corresponding filesystem call. Read operations return maps, JSON objects, JSON strings, or streams. Write operations often return `Void` or a boolean JSON object. `copyBytes()` streams upload bodies into filesystem output streams using the configured buffer and closes both streams in a finally block.

## State and Persistence Behavior
The only shared mutable class state is static `bufferSize`, initialized from `httpfs.buffer.size` by `HttpFSServerWebApp`. Persistent changes are delegated to the target `FileSystem`: file creation/appending/deletion, directory creation, rename, ACL/xattr/storage-policy/snapshot/EC-policy mutations, and metadata changes. Metrics counters in `HttpFSServerMetrics` are incremented for selected operations and byte counts.

## Dependencies and Integration Points
The class depends on Hadoop `FileSystem`, HDFS-specific APIs (`DistributedFileSystem`, snapshots, erasure coding, storage policies), Ozone HttpFS constants, Json-simple, Jackson-facing `JsonUtil`, and the gateway singleton `HttpFSServerWebApp` for metrics. Some operations require the underlying filesystem to be a `DistributedFileSystem`; otherwise they throw `UnsupportedOperationException`.

## Risks and Edge Cases
Because several operations cast or require HDFS-specific types, compatibility with non-HDFS/Ozone filesystem implementations can be partial. `storagePolicyToJSON()` casts `BlockStoragePolicySpi` to HDFS `BlockStoragePolicy`. `copyBytes()` always closes streams, matching previous IOUtils behavior but requiring callers not to reuse request streams. Some metrics are absent for metadata operations. File checksum serialization assumes a non-null checksum. Batched listing clones the token but would throw if constructed with null.

## Test Signals
This subset does not include direct tests for `FSOperations`. The class is heavily integration-oriented; meaningful tests need mocked `FileSystem` executors and/or HttpFS endpoint tests for each operation family, especially upload streaming, JSON compatibility, and unsupported filesystem cases.
