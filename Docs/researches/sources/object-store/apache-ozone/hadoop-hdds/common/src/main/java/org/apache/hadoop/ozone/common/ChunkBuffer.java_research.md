# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ozone/common/ChunkBuffer.java

## Purpose

`ChunkBuffer` is the common abstraction Ozone uses for block chunk payload buffers. It deliberately presents a `ByteBuffer`-like API while hiding whether data is stored in one direct buffer, a list of buffers, or an incrementally allocated sequence. It also extends `ChunkBufferToByteString` for protobuf/Ratis conversion and `UncheckedAutoCloseable` so direct `CodecBuffer` resources can be released.

## APIs and control flow

Static factories choose the backing implementation: `allocate(capacity)` allocates one direct `CodecBuffer`; `allocate(capacity, increment)` uses `IncrementalChunkBuffer` when the increment is positive and smaller than the capacity; `wrap(ByteBuffer)` and `wrap(List<ByteBuffer>)` adapt existing buffers. The core API mirrors `position`, `remaining`, `limit`, `rewind`, `clear`, `put`, `duplicate`, `iterate`, `asByteBufferList`, and `writeTo`.

## State, dependencies, and integration

The interface owns no state, but its contracts are position-sensitive. Default `put` overloads convert byte arrays and Ratis `ByteString` into `ByteBuffer` writes. It depends on HDDS `CodecBuffer`, Ratis `ByteString`, and `GatheringByteChannel`, and is integrated by container IO and checksum paths that need efficient chunk transfer.

## Risks and test signals

The main risk is callers assuming immutable or thread-safe behavior. Implementations mutate backing buffer positions during writes and iteration. Tests should cover allocation choice, duplicate bounds, list wrapping, close/release behavior, and preservation of buffer position during ByteString conversion.
