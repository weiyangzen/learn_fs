# sources/object-store/apache-ozone/hadoop-ozone/interface-storage/src/test/java/org/apache/hadoop/ozone/om/helpers/TestRepeatedOmKeyInfoCodec.java

Purpose: Unit test for `RepeatedOmKeyInfo.getCodec(boolean)`, covering pipeline stripping, compatibility with pipeline-bearing encodings, bucket ID persistence, and basic thread-safety.

Important APIs/types/functions: Extends `Proto2CodecTestBase<RepeatedOmKeyInfo>`, default codec is `getCodec(true)`. Builds `OmKeyInfo` objects with random pipelines and block locations. Tests `threadSafety`, `testWithoutPipeline`, and `testCompatibility` for one and two chunks.

Control flow, state, and persistence: Serializes deleted/repeated key info with a bucket ID. The no-pipeline codec strips pipeline data on write. Compatibility test writes with pipeline-retaining codec and reads with no-pipeline codec, asserting pipeline is preserved when present in stored bytes. Thread-safety test concurrently serializes copied objects while mutating the original repeated key list.

Dependencies and integration points: Uses HDDS pipelines, Ratis replication config, `RepeatedOmKeyInfo`, deleted-key table semantics, Guava `ThreadFactoryBuilder`, and JUnit.

Risks: Thread-safety check is timing-based and daemon-thread based, so it can miss rare races. The serialization loop is high count and could be expensive in constrained environments.

Test signals: Good signal for deleted-key codec compatibility across old/new persisted formats and concurrent copy/serialization behavior.
