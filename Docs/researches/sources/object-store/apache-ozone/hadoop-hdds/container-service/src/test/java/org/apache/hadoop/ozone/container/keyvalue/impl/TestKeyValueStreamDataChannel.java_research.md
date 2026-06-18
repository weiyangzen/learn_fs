# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/keyvalue/impl/TestKeyValueStreamDataChannel.java

## Purpose
`TestKeyValueStreamDataChannel` verifies the Ratis data-stream write path used for streamed key-value writes. It tests serialization of appended `PutBlock` requests, space-availability failure behavior, buffer splitting/reassembly, and close-time extraction of the trailing put-block proto.

## Important APIs, types, and functions
The suite exercises `KeyValueStreamDataChannel.readProtoLength`, `writeBuffers`, `writeFully`, `assertSpaceAvailability`, and `write`, plus static helpers from `BlockDataStreamOutput`: `PUT_BLOCK_REQUEST_LENGTH_MAX`, `executePutBlockClose`, and `getProtoLength`. It defines test `Output` and `Reply` implementations of Ratis `DataStreamOutput` and `DataStreamReply`.

## Control flow
`testSerialization` builds a data buffer followed by the serialized `PUT_BLOCK_PROTO` and four-byte proto length, then reads the request back and rewinds the `ByteBuf` writer index to expose only data. `testVolumeFullCase` constructs a channel over a temp file with a mocked full `HddsVolume`, expecting `StorageContainerException` both from explicit space checking and `write`. `testBuffers` runs many combinations of output buffer max size and data size in parallel, writing random byte ranges and then closing with `executePutBlockClose`.

## State and persistence behavior
The in-memory `ByteBuf` in `Output` collects only application data; the appended put-block request is consumed at close and not left in the data output. The volume-full test checks no write proceeds when the mocked volume has zero available capacity. Reference-counted buffers are retained and released around write calls.

## Dependencies and integration points
This file integrates Ozone container command protobufs, Ratis `ContainerCommandRequestMessage`, Netty `ByteBuf`, Ratis stream APIs, volume usage, and container metrics. It protects the wire-format contract between streaming data and terminal put-block metadata.

## Risks and edge cases
Risks include miscomputing the four-byte proto length location, corrupting data when writes split across buffer boundaries, writing put-block bytes into user data, leaking reference-counted buffers, and allowing stream writes when a container volume is full.

## Test signals
Signals include exact proto equality, output data byte-for-byte equality, successful replies with correct bytes written, close replies carrying the parsed put-block request, and exceptions for full-volume writes.
