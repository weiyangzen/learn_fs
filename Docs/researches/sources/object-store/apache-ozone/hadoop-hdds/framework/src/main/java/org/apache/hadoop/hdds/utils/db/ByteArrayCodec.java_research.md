# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/db/ByteArrayCodec.java

## Purpose
`ByteArrayCodec` is a singleton no-op codec for byte arrays. It allows raw byte keys or values to pass through typed table APIs without serialization overhead.

## Important APIs and Types
`get()` returns the singleton `Codec<byte[]>`. `getTypeClass` returns `byte[].class`. `toPersistedFormat`, `fromPersistedFormat`, and `copyObject` all return the same array reference.

## Control Flow and State
The class is immutable and stateless. There is no null handling beyond returning whatever reference is passed.

## Persistence, Dependencies, and Integration
It implements the HDDS `Codec` interface and is registered by default in `CodecRegistry`. It is used by raw RocksDB tables and byte-array typed metadata tables.

## Risks and Test Signals
Returning the same mutable array is efficient but can leak mutations between caller, cache, and persistence layers. Tests should verify pass-through behavior and document aliasing expectations; callers needing defensive copies must use a different codec or copy externally.
