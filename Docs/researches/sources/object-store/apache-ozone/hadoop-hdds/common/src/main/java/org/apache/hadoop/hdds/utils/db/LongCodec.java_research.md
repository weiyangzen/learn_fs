# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/utils/db/LongCodec.java

## Purpose
Serializes `Long` values as eight-byte big-endian data.

## Important APIs, Types, And Functions
Singleton `LongCodec.get()` implements `Codec<Long>`, supports `CodecBuffer`, and provides `toByteArray(long)` and `fromByteArray(byte[])`.

## Control Flow
Buffer path writes `putLong` into an eight-byte buffer. Byte-array path returns null for null object and otherwise writes/reads via `ByteBuffer`.

## State And Persistence
No mutable state. Persistent format is Java `ByteBuffer` big-endian long encoding.

## Dependencies And Integration Points
Used by DB tables needing numeric key/value codecs with direct buffer support.

## Risks
Malformed byte-array lengths are not explicitly checked; short arrays throw and extra bytes are ignored. Null handling differs from non-null interface comments.

## Test Signals
Round trips should cover zero, negative, min/max, null byte-array values, direct/heap buffer paths, and invalid lengths.
