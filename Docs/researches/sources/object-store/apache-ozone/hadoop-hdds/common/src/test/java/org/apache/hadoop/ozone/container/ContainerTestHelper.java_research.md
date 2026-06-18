# sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/ozone/container/ContainerTestHelper.java

## Purpose
Provides a large collection of static helpers for building container protocol requests, responses, block/chunk metadata, data buffers, checksums, pipelines, and temporary files for Ozone container tests.

## Important APIs, types, and functions
- Helpers include `getChunk`, `getData`, `setDataChecksum`, `getWriteChunkRequest`, `getListBlockRequest`, `getPutBlockRequest`, `newWriteChunkRequestBuilder`, `getWriteSmallFileRequest`, `getReadSmallFileRequest`, `getReadChunkRequest`, `newReadChunkRequestBuilder`, `getCreateContainerRequest`, `getCreateContainerSecureRequest`, `getUpdateContainerRequest`, `getCreateContainerResponse`, and further response/request builders.
- Uses container protobufs such as `ContainerCommandRequestProto`, `ContainerCommandResponseProto`, `DatanodeBlockID`, `KeyValue`, checksum fields, and command-specific request/response types.
- Uses `BlockID`, container `BlockData`, `ChunkInfo`, `Checksum`, `ChunkBuffer`, `ClientVersion`, `Token`, `UniqueId`, `Pipeline`, and `MockPipeline`.

## Control flow
Most helpers build valid protobuf request builders from IDs, pipeline metadata, datanode UUIDs, block IDs, chunk data, checksums, and optional tokens. Data helpers create random buffers and reset positions after checksum computation. File helpers write/read temporary data for tests that need on-disk chunk content.

## State and persistence behavior
The helper mostly creates in-memory protocol objects, but some methods write temporary files or read file contents. Static constants provide dummy container and datanode IDs for repeatable test construction.

## Dependencies and integration points
This is central shared test infrastructure for Ozone container, datanode, and client command tests. It integrates SCM pipeline helpers, container common helper classes, protobuf protocol definitions, checksum logic, and security tokens.

## Risks and test signals
Because many tests depend on these builders, incorrect defaults can create unrealistic requests or hide protocol changes. Key risks are stale client-version fields, missing checksum data, wrong block/chunk IDs, and helper-generated requests that diverge from production client behavior.
