# sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/hdds/utils/db/Proto2CodecTestBase.java

## Purpose
Abstract base test for protobuf-v2-backed `Codec` implementations.

## Important APIs, types, and functions
- Requires subclasses to provide `getCodec`.
- Tests invalid protobuf bytes, `fromPersistedFormat`, and `toPersistedFormat`.
- Uses `InvalidProtocolBufferException` and JUnit assertions.

## Control flow
The base tests feed invalid bytes to the codec and expect parse failure, then exercise serialization and deserialization of valid subclass-provided values through the codec contract.

## State and persistence behavior
Serialized byte arrays model persisted database values. No external DB is used.

## Dependencies and integration points
Subclasses can inherit these tests to validate HDDS protobuf codecs used by metadata tables.

## Risks and test signals
A codec that accepts invalid bytes or emits non-round-trippable data can corrupt metadata reads. This base class signals core protobuf codec correctness.
