# sources/object-store/apache-ozone/hadoop-ozone/interface-storage/src/test/java/org/apache/hadoop/ozone/om/helpers/TestOmMultipartKeyInfoCodec.java

Purpose: Unit test for `OmMultipartKeyInfo.getCodec()` serialization and invalid-data handling.

Important APIs/types/functions: Extends `Proto2CodecTestBase<OmMultipartKeyInfo>`, returns `OmMultipartKeyInfo.getCodec()`, creates an object with random upload ID, creation time, and Ratis THREE replication config.

Control flow, state, and persistence: The test serializes a multipart key info object, deserializes it, and asserts equality. It then attempts to parse random UTF-8 bytes and expects an `IllegalArgumentException` with a specific message.

Dependencies and integration points: Uses HDDS replication proto, Ozone multipart helper, AssertJ/JUnit, and codec base tests. It validates OM multipart upload table value persistence.

Risks: Catches and prints unexpected `IOException`s instead of failing immediately in some branches, which can weaken failure clarity if an exception leaves data null in unexpected ways. The exact invalid-data message is brittle.

Test signals: Positive round-trip signal and negative malformed-input signal for multipart key codec.
