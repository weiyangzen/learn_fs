# sources/object-store/apache-ozone/hadoop-ozone/interface-storage/src/test/java/org/apache/hadoop/ozone/om/helpers/TestOmPrefixInfoCodec.java

Purpose: Unit test for `OmPrefixInfo.getCodec()` persisted bytes round trip.

Important APIs/types/functions: Extends `Proto2CodecTestBase<OmPrefixInfo>`, returns `OmPrefixInfo.getCodec()`, creates a prefix `/user/hive/warehouse` with a user ACL and metadata `id=100`.

Control flow, state, and persistence: Serializes the `OmPrefixInfo` with the codec, deserializes it, and asserts exact object equality.

Dependencies and integration points: Uses `OzoneAcl`, ACL identity/type enums, metadata builder methods, and HDDS codec base. It validates persisted prefix table values.

Risks: Covers a single happy-path ACL and metadata record. Does not explicitly test malformed bytes beyond inherited base tests.

Test signals: Direct codec round-trip coverage for prefix metadata persistence.
