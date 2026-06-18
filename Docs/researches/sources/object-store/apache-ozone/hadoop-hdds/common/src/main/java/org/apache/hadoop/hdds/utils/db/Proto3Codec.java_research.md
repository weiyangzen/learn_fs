# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/utils/db/Proto3Codec.java

## Purpose
Provides cached codecs for Ratis-shaded protobuf v3 `MessageLite` messages.

## Important APIs, Types, And Functions
Static `get(T)` and `get(T, boolean allowInvalidProtocolBufferException)` return codecs. Methods support `CodecBuffer`, byte-array serialization, parsing from read-only `ByteBuffer`, and immutable copy behavior.

## Control Flow
The first call per class populates a `ConcurrentHashMap`. Buffer serialization allocates serialized size and writes through shaded `CodedOutputStream.newInstance(ByteBuffer)`. Deserialization returns null on parse error when `allowInvalidProtocolBufferException` is true; otherwise it throws or wraps the parse exception.

## State And Persistence
State is the static class-to-codec cache and per-codec parser flag. Persisted format is standard shaded protobuf bytes.

## Dependencies And Integration Points
Depends on Ratis-shaded protobuf APIs and Ozone codec infrastructure. Used for Ratis/HDDS proto3 metadata without mixing unshaded proto classes.

## Risks
The cache is keyed only by class, so the first `allowInvalidProtocolBufferException` value wins for that class; later callers requesting a different behavior may not get it. Returning null on invalid bytes can mask corruption if used outside tolerant paths.

## Test Signals
Tests should cover parse failure with both allow modes, cache behavior when modes differ, buffer and byte-array round trips, and direct/heap leak checks.
