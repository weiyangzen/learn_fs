# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/utils/db/BooleanCodec.java

## Purpose
Serializes Java `Boolean` values for metadata stores.

## Important APIs, Types, And Functions
Singleton `BooleanCodec.get()` implements `Codec<Boolean>`. It supports `CodecBuffer`, writes one byte, reads one byte, and returns immutable booleans directly from `copyObject`.

## Control Flow
`toCodecBuffer()` allocates one byte and writes `1`; `toPersistedFormat()` writes `1` or `0`. Deserialization requires byte-array length one for persisted format; buffer format reads one byte and compares to `1`.

## State And Persistence
No mutable codec state. Persistent bytes are single-byte boolean encodings.

## Dependencies And Integration Points
Integrates with the shared `Codec` and `CodecBuffer` abstraction used by RocksDB table codecs.

## Risks
`toCodecBuffer(Boolean object, ...)` writes `TRUE` regardless of `object`, which differs from `toPersistedFormat()` and is a high-value bug signal unless callers never use buffer serialization for false. Deserialization treats any non-`1` value as false.

## Test Signals
Codec round-trip tests should explicitly include `false` through both byte-array and `CodecBuffer` paths. `CodecTestUtil`-style buffer leak checks apply.
