# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/utils/db/UuidCodec.java

## Purpose
Serializes Java `UUID` values as fixed 16-byte big-endian most/least significant bits.

## Important APIs, Types, And Functions
Singleton `UuidCodec.get()` implements `Codec<UUID>`. `getSerializedSize()` returns 16. Buffer and byte-array paths write/read two longs.

## Control Flow
Serialization writes `getMostSignificantBits()` then `getLeastSignificantBits()`. Deserialization validates byte-array length exactly 16 and constructs a new `UUID` from two longs.

## State And Persistence
No mutable state. Persistent layout is a stable 16-byte UUID representation.

## Dependencies And Integration Points
Used for DB keys/values needing compact UUID storage and direct-buffer support.

## Risks
Only byte-array deserialization checks exact length; buffer deserialization assumes enough readable bytes and ignores trailing bytes. Null UUIDs are not supported.

## Test Signals
Round trips should cover random UUIDs, all-zero UUID, max UUID, invalid lengths, and heap/direct `CodecBuffer`.
