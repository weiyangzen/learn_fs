# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/scm/ha/SequenceIdType.java

## Purpose

`SequenceIdType` enumerates persisted sequence counters managed by SCM HA sequence ID generation. Enum names are intentionally persisted RocksDB keys.

## Important APIs, Types, and Functions

Constants include `localId`, `delTxnId`, `containerId`, `CertificateId`, and deprecated `rootCertificateId`. `getCodec()` returns a custom `Codec<SequenceIdType>` supporting byte arrays and `CodecBuffer`.

## Control Flow

Each enum constant encodes its name with `StringCodec`. Decoding uses the first byte as a fast lookup, then verifies full byte equality. Static initialization ensures first-byte uniqueness across constants.

## State and Persistence Behavior

Persisted state is the enum name bytes stored as RocksDB keys in the sequence ID table. Byte arrays are cloned and byte buffers duplicated for safety.

## Dependencies and Integration Points

Used by `SCMMetadataStore.getSequenceIdTable()` and sequence ID generation. Depends on HDDS DB codec abstractions.

## Risks and Test Signals

Renaming enum constants or adding one with duplicate first byte can break persisted compatibility or class initialization. Tests should cover codec byte and buffer round trips, unknown bytes, deprecated key compatibility, and static uniqueness.
