# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/protocolPB/OMPBHelper.java

Purpose: Utility class for converting common OM protocol values between Hadoop/Ozone Java objects and protobuf representations, plus safe debug rendering of OM messages.

Important APIs and types: Token conversion `tokenFromProto`/`protoFromToken`; bucket and file encryption conversions; file checksum conversions for `MD5MD5CRC32FileChecksum` and `CompositeCrcFileChecksum`; cipher suite and crypto protocol version enum conversions; `processForDebug(OMRequest/OMResponse)`. `REDACTED` is used to hide DB update payloads.

Control flow: Conversion methods validate nulls where required, build protobuf messages or Java helper objects, and switch over checksum/cipher/protocol enum types. MD5 checksum conversion reads the serialized Hadoop checksum layout to extract bytes-per-CRC, CRC-per-block, and MD5. Response debug rendering clones DB update responses and replaces data entries with a redacted marker before formatting.

State and persistence behavior: Stateless static helper. It does not persist data but affects serialized wire/storage forms for tokens, encryption info, and checksums.

Dependencies and integration points: Used by OM client translator token APIs, block/delegation token code, encrypted bucket/key handling, checksum APIs, and debug logging. It depends on Hadoop crypto/checksum classes, Ozone checksum helpers, protobuf classes, and SCM PB helper ByteString utilities.

Risks: Checksum conversion is wire-compatibility-sensitive. There is explicit compatibility handling for a fixed HDDS-12954 bug where proto MD5 could be stored in a 20-byte buffer. Unsupported checksum runtime types log warnings and return null, which callers must tolerate. Enum conversions return `null` for unknown Java enum defaults in some directions.

Test signals: Round-trip tests for tokens, bucket/file encryption info, MD5 CRC32/CRC32C checksums, composite CRC checksums, unknown cipher/protocol handling, legacy oversized MD5 proto input, null validation, and DB update redaction in debug strings.
