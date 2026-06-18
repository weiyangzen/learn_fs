# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/container/common/helpers/ChunkInfo.java

## Purpose

`ChunkInfo` is the Java helper for `ContainerProtos.ChunkInfo`. It represents a physical chunk name, offset, length, checksum data, metadata, optional stripe checksum, and a compatibility flag for older read wire formats.

## APIs and control flow

Construction sets immutable chunk identity fields and a sorted metadata map. `addMetadata` synchronizes on the map and rejects duplicate keys. `getFromProtoBuf` requires a non-null proto, copies metadata, converts checksum data with `ChecksumData.getFromProtoBuf`, and captures `stripeChecksum` when present. `getProtoBufMessage` writes chunk identity, metadata, and checksum data, using `Checksum.getNoChecksumDataProto()` when no checksum is set.

## State, dependencies, and integration

State is mostly immutable chunk identity plus mutable checksum, metadata, stripe checksum, and `readDataIntoSingleBuffer`. It depends on container protobufs, Ozone `Checksum`/`ChecksumData`, and Ratis `ByteString`. It integrates with container protocol messages and chunk read/write helpers.

## Risks and test signals

The current `getProtoBufMessage` does not write `stripeChecksum` back into the builder, while `getFromProtoBuf` reads it. That asymmetry is a persistence risk if callers expect round-trip preservation. Tests should cover duplicate metadata, null checksum fallback, proto conversion, stripe checksum round trip, and old-client single-buffer flag behavior.
