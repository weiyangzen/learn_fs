# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/utils/db/IntegerCodec.java

## Purpose
Serializes `Integer` values as four-byte big-endian data.

## Important APIs, Types, And Functions
Singleton `IntegerCodec.get()` implements `Codec<Integer>`, supports `CodecBuffer`, and exposes helpers `toByteArray(int)` and `fromByteArray(byte[])`.

## Control Flow
Buffer encoding allocates `Integer.BYTES` and writes `putInt`. Byte-array encoding returns null for null object or wraps a four-byte array and writes the value. Deserialization wraps input bytes and reads `getInt`.

## State And Persistence
No mutable state. Persistent format is Java `ByteBuffer` big-endian integer encoding.

## Dependencies And Integration Points
Used for DB keys/values that need stable numeric byte representations and direct-buffer serialization.

## Risks
`fromByteArray` does not validate exact length beyond `ByteBuffer.getInt()` behavior; extra bytes are ignored and short arrays throw runtime exceptions. Null persisted values are allowed here.

## Test Signals
Codec round-trip tests should include positive, negative, zero, min/max, null byte-array path, and malformed lengths.
