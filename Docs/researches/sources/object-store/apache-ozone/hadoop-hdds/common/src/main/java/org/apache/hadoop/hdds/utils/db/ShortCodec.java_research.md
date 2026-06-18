# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/utils/db/ShortCodec.java

## Purpose
Serializes `Short` values as two-byte big-endian data.

## Important APIs, Types, And Functions
Singleton `ShortCodec.get()` implements `Codec<Short>` and supports `CodecBuffer`.

## Control Flow
Buffer serialization writes `putShort` into a two-byte buffer. Byte-array serialization wraps a two-byte array and writes the short. Deserialization reads `getShort`.

## State And Persistence
No mutable state. Persistent format is Java `ByteBuffer` big-endian short encoding.

## Dependencies And Integration Points
Used for DB metadata fields that need compact numeric encoding.

## Risks
Unlike `IntegerCodec` and `LongCodec`, `toPersistedFormat` does not accept null. Length validation is implicit through `ByteBuffer`, so extra bytes are ignored and short arrays fail at runtime.

## Test Signals
Round trips should cover min/max, negative, zero, direct/heap buffers, null handling, and malformed byte lengths.
