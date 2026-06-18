# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/db/ByteStringCodec.java

## Purpose
`ByteStringCodec` serializes and deserializes protobuf `ByteString` values for HDDS metadata tables, including optimized `CodecBuffer` support.

## Important APIs and Types
`get()` returns the singleton. `supportCodecBuffer` returns true. `toCodecBuffer` wraps existing `ByteString` data or copies into a direct buffer when requested. `fromCodecBuffer` returns the wrapped `ByteString` when possible or copies from a read-only byte buffer. Byte-array conversion maps null inputs to empty values.

## Control Flow and State
The class is stateless. It tries to avoid copies when buffer/directness constraints allow, while preserving compatibility with direct allocators.

## Persistence, Dependencies, and Integration
It depends on protobuf `ByteString`, `jakarta.annotation.Nonnull`, and HDDS `CodecBuffer`. It integrates with typed table values storing protobuf blobs and with code paths using direct buffers for RocksDB writes.

## Risks and Test Signals
Null object serialization returns an empty byte array, which differs from codecs that reject null persistence. Direct allocator behavior should be tested carefully to avoid heap/direct mismatches. Tests should cover nulls, empty values, direct and heap `CodecBuffer` round trips, wrapped-object preservation, and immutability assumptions.
