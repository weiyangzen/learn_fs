# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/container/common/helpers/BlockData.java

## Purpose

`BlockData` is the Java helper and DB codec wrapper for `ContainerProtos.BlockData`. It records a `BlockID`, metadata, chunk list, block size, and block commit sequence ID while preserving protobuf compatibility.

## APIs and control flow

`getCodec()` returns a `DelegatedCodec` over a proto3 codec with backward compatibility for schema-one parsing. `getFromProtoBuf` converts metadata and chunks, then validates any proto `size` field against computed chunk length. `getProtoBufMessage` recomputes chunk length and throws `CodecException` if it differs from the stored size. `addMetadata` rejects duplicate keys. `addChunk`, `removeChunk`, and `setChunks` maintain size as chunks change. `getChunks` uses a memory-saving internal representation: null for none, a single proto object for one chunk, and a list for many.

## State, dependencies, and integration

State includes mutable `BlockID`, sorted metadata, compact `chunkList`, and `size`. It depends on HDDS `BlockID`, container protobufs, HDDS codec classes, `OzoneConsts`, and Ratis `TextFormat`. It integrates with datanode container metadata tables and block commit/read paths.

## Risks and test signals

The compact `Object` chunk representation is efficient but type-sensitive. External chunk lists passed to `setChunks` can be retained directly when size is greater than one. Tests should cover codec round trips, duplicate metadata rejection, size mismatch failures, single-to-list transitions, removal size updates, and block group length metadata parsing.
