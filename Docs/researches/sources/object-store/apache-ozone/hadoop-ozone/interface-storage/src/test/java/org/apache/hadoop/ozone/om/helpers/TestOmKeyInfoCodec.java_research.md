# sources/object-store/apache-ozone/hadoop-ozone/interface-storage/src/test/java/org/apache/hadoop/ozone/om/helpers/TestOmKeyInfoCodec.java

Purpose: Unit test for `OmKeyInfo.getCodec()` persisted-format behavior, especially pipeline elision and file checksum preservation.

Important APIs/types/functions: Extends `Proto2CodecTestBase<OmKeyInfo>`, returns `OmKeyInfo.getCodec()`, constructs `OmKeyInfo` with random HDDS pipeline/block locations, Ratis replication config, metadata, and an empty `MD5MD5CRC32GzipFileChecksum`. `test()` runs round trips with one and two chunks.

Control flow, state, and persistence: The test serializes an `OmKeyInfo` to persisted bytes and deserializes it. It asserts that persisted key locations do not retain pipeline objects and that file checksum survives the codec round trip.

Dependencies and integration points: Uses HDDS test pipeline utilities, `BlockID`, `OmKeyLocationInfo`, `OmKeyLocationInfoGroup`, Hadoop `FileChecksum`, and JUnit. It validates DB-storage behavior for key metadata.

Risks: Test prints serialized size to stdout, which is noisy but useful for manual observation. It focuses on latest version first location and may not cover multi-version edge cases.

Test signals: Direct positive signal for key codec pipeline stripping and checksum persistence. Inherits invalid-protobuf behavior checks from `Proto2CodecTestBase` unless overridden upstream.
