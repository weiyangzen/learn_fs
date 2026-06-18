# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/db/CodecBufferCodec.java

## Purpose
`CodecBufferCodec` persists `CodecBuffer` objects directly, preserving direct-vs-heap allocation mode and avoiding unnecessary copies for buffer-native table operations.

## Important APIs and Types
`get(boolean direct)` returns either the direct or heap singleton. `supportCodecBuffer` returns true. `toCodecBuffer` requires the provided allocator to match the object's directness and returns the same object. `fromPersistedFormat` allocates a new buffer of the configured type and fills it from a byte array. `copyObject` also returns the same buffer.

## Control Flow and State
Each singleton stores a `CodecBuffer.Allocator`. Serialization reads `buffer.getArray()`, while deserialization wraps the input bytes in a `ByteBuffer` and puts them into a newly allocated `CodecBuffer`.

## Persistence, Dependencies, and Integration
It depends on `CodecBuffer`, `ByteBuffer`, and Jakarta `Nonnull`. It is useful for RocksDB paths that already operate on direct buffers.

## Risks and Test Signals
The class intentionally does not copy in `copyObject` or `toCodecBuffer`, so ownership/lifecycle is caller-sensitive. `getArray()` may imply heap accessibility depending on `CodecBuffer` implementation. Tests should cover direct/heap mismatch exceptions, round trips, close ownership expectations, and mutation/aliasing behavior.
