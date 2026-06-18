# sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/hdds/ratis/TestContainerCommandRequestMessage.java

## Purpose
Tests `ContainerCommandRequestMessage` serialization behavior for container write requests that carry block, chunk, checksum, and small-file payload data through the Ratis request-message layer.

## Important APIs, types, and functions
- Uses `ContainerCommandRequestProto`, `PutSmallFileRequestProto`, `WriteChunkRequestProto`, `PutBlockRequestProto`, `BlockData`, `ChunkInfo`, `KeyValue`, and `BlockID` from the HDDS container protocol.
- Exercises `ContainerCommandRequestMessage.toMessage(...)` and message reconstruction paths around protobuf payloads and `ByteString` data.
- Builds checksum metadata through `Checksum` and `ChecksumData` using `ChecksumType`, with `ClientVersion` included in request construction.
- Test cases are `testPutSmallFile` and `testWriteChunk`.

## Control flow
The tests build randomized byte payloads, compute or attach checksum data, wrap the payload in the relevant container command request, convert it to a Ratis message, then deserialize and compare command fields and embedded data. The small-file path nests chunk and block metadata inside the `PutSmallFile` request, while the write-chunk path focuses on a separate chunk write request.

## State and persistence behavior
The file does not persist data to disk. State is local to generated protobuf builders, random payload arrays, checksum objects, and reconstructed message instances.

## Dependencies and integration points
This test bridges HDDS container protobufs, Ozone checksum code, and Apache Ratis message transport. It is a regression signal for datanode container command replication over Ratis.

## Risks and test signals
The main risk is losing payload bytes or checksum/block metadata during request wrapping. The tests signal that small-file and write-chunk commands preserve command type, block identifiers, chunk metadata, key-values, and data bytes after Ratis message conversion.
