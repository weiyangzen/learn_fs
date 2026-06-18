## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/metadata/SchemaOneChunkInfoListCodec.java

Purpose: Provides a schema-one-compatible codec for deleted-block values that may contain either modern chunk info protobufs or legacy non-protobuf placeholders.

Important APIs and functions: `get()` returns the singleton codec. `toPersistedFormat()` serializes `ChunkInfoList` protobuf bytes. `fromPersistedFormat()` attempts to parse `ContainerProtos.ChunkInfoList`; on parse failure it logs a warning once and returns null. `copyObject()` is unsupported.

Control flow and state: The codec has singleton state and an `AtomicBoolean LOGGED` to avoid repeated warnings for legacy data. Decode failure is not thrown to callers; it returns null to reflect absent chunk information.

Persistence and dependencies: Used by schema-one deleted-block logical table over the default CF. Depends on container protobufs, `ChunkInfoList`, HDDS `Codec`, and protobuf parse exceptions.

Risks: Returning null for invalid data requires callers to tolerate absent chunk info. `copyObject()` unsupported can break generic code that assumes all codecs copy. Parse failure could also indicate corruption, not just legacy format, but the codec treats both as missing chunk info.

Test signals: Encode/decode valid chunk lists, decode legacy long/random bytes to null with one warning, verify singleton behavior, and ensure deleted-block table users handle null values.
