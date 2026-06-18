# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/container/common/helpers/ChunkInfoList.java

## Purpose

`ChunkInfoList` is an immutable wrapper and codec target for a list of `ContainerProtos.ChunkInfo` messages.

## APIs and control flow

The constructor stores `Collections.unmodifiableList(chunks)`. `getCodec()` returns a shallow-copy `DelegatedCodec` over `ContainerProtos.ChunkInfoList`. `getFromProtoBuf` wraps `chunksProto.getChunksList()`, and `getProtoBufMessage` builds a proto by adding all wrapped chunks.

## State, dependencies, and integration

State is the unmodifiable chunk list reference. Dependencies are container protobufs and HDDS codec utilities. It integrates with metadata tables or protocol helpers that persist chunk lists as a single value.

## Risks and test signals

The constructor does not null-check or defensively copy, so mutations to a caller-owned mutable list can affect the wrapper despite the unmodifiable view. Tests should cover codec round trips, null rejection expectations, shallow-copy behavior, and immutability through the public accessor surface.
