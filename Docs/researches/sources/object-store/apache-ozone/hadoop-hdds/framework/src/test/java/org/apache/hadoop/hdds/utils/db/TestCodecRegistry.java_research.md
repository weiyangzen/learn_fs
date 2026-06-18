<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/utils/db/TestCodecRegistry.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/utils/db/TestCodecRegistry.java

Purpose: verifies `CodecRegistry` resolves codecs by object instance and by Java class.

Important APIs/types/functions: `CodecRegistry.newBuilder`, `addCodec`, `getCodec`, `getCodecFromClass`, `IntegerCodec`, `LongCodec`, `StringCodec`, `ByteArrayCodec`, `ByteStringCodec`, `Codec.EMPTY_BYTE_ARRAY`, and protobuf `ByteString.EMPTY`.

Control flow: a registry is built with a ByteString codec in addition to defaults. Helper methods retrieve a codec for an object or class and assert the exact codec class. Tests cover integer, long, string, byte array, and ByteString values/classes.

State and persistence behavior: registry state is in-memory codec mappings. No persistence.

Dependencies and integration points: validates DB serialization infrastructure that dynamically selects codecs for table key/value types.

Risks: exact-class assertions mean subclass/proxy behavior is not covered. Missing mappings would fail table initialization or runtime serialization.

Test signals: asserts resolved codec is an instance of and exactly the expected codec class for each supported type.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/utils/db/TestCodecRegistry.java -->
