# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/utils/db/Codec.java

## Purpose
Defines the serialization contract for converting Java metadata objects to persisted bytes and optional `CodecBuffer` instances.

## Important APIs, Types, And Functions
Key methods are `getTypeClass`, `supportCodecBuffer`, `toCodecBuffer`, `toDirectCodecBuffer`, `toHeapCodecBuffer`, `fromCodecBuffer`, `toPersistedFormat`, `toPersistedFormatImpl`, `fromPersistedFormat`, `fromPersistedFormatImpl`, and `copyObject`.

## Control Flow
Default buffer methods throw unless an implementation opts in. Default byte-array methods null-check inputs, delegate to `Impl` methods, and wrap failures in `CodecException` with type/length context.

## State And Persistence
The interface owns no state. Implementations define persisted byte layout and copy semantics for DB keys/values.

## Dependencies And Integration Points
Used by table, cache, and RocksDB layers throughout HDDS/Ozone. `CodecBuffer` support enables direct-buffer DB APIs and reduced copying.

## Risks
Implementations must keep byte-array and buffer encodings consistent. Some primitive codecs permit null byte-array serialization despite the interface comment saying objects should not be null. Incorrect `copyObject` semantics can expose mutable DB cache state.

## Test Signals
`CodecTestUtil` exercises byte-array and `CodecBuffer` round trips, copy behavior, old-codec compatibility, and leak checks. Every codec should use it for both heap and direct buffers where supported.
