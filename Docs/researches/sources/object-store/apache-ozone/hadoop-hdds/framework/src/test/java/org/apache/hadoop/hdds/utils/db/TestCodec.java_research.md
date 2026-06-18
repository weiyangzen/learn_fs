<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/utils/db/TestCodec.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/utils/db/TestCodec.java

Purpose: broad test coverage for HDDS `Codec` implementations and `CodecBuffer` serialization paths.

Important APIs/types/functions: `Codec`, `ShortCodec`, `IntegerCodec`, `LongCodec`, `StringCodec`, `FixedLengthStringCodec`, `ByteStringCodec`, `UuidCodec`, `CodecBuffer`, `CodecTestUtil.runTest`, `RDBBatchOperation.Bytes`, Guava primitive byte conversions, protobuf `ByteString`, and RocksDB native library loading.

Control flow: static setup enables leak detection and loads RocksDB. Numeric codec tests cover edge values and random values, comparing persisted bytes to Guava conversions. String tests cover ASCII, multilingual UTF-8, malformed UTF-8 fallback/no-fallback behavior, and serialized-size expectations. Fixed-length string tests require ASCII and reject multibyte characters. ByteString and UUID tests round-trip empty, random, multilingual, and edge values. Shared `runTest` validates byte-array and heap/direct `CodecBuffer` forms.

State and persistence behavior: no external persistence; serialization produces byte arrays and buffers. Direct buffers are closed in try-with-resources and leak detection is exercised through `gc`.

Dependencies and integration points: integrates codec implementations with RocksDB batch byte wrappers, direct/heap buffer allocators, Guava/protobuf byte formats, and codec test utilities.

Risks: direct buffer lifecycle is important; leaks can destabilize native memory. UTF-8 malformed behavior differs between fallback and no-fallback codecs and is compatibility-sensitive. Fixed-length codec rejects multibyte strings by design.

Test signals: asserts round-trip equality, serialized sizes, byte compatibility with Guava primitives, malformed UTF-8 exception/fallback behavior, fixed-length status, multibyte rejection for fixed-length strings, direct empty buffer behavior, UUID size, and equality/hash consistency for array-vs-buffer `Bytes`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/utils/db/TestCodec.java -->
