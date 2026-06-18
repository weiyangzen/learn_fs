# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/utils/db/Proto2Codec.java

## Purpose
Provides cached codecs for `com.google.protobuf.MessageLite` protobuf v2 messages.

## Important APIs, Types, And Functions
Static `get(T t)` returns a cached codec keyed by message class. Each codec stores message class and parser. It supports `CodecBuffer`, byte-array serialization, parsing, and immutable copy semantics.

## Control Flow
`get()` uses `ConcurrentHashMap.computeIfAbsent`. Buffer serialization precomputes serialized size, allocates that exact size, and writes via `message.writeTo(OutputStream)`. Buffer parsing reads through `ByteBufInputStream` and closes it. Byte-array parsing delegates to `parser.parseFrom`.

## State And Persistence
State is the static class-to-codec cache and immutable parser metadata. Persisted format is standard protobuf bytes.

## Dependencies And Integration Points
Depends on unshaded Google protobuf v2 APIs, `CodecBuffer`, and HDDS `IOUtils`. Used for legacy protobuf metadata types.

## Risks
Cache keys ignore parser options beyond class. Parse errors are wrapped as `CodecException` on buffer path and via interface wrapping on byte-array path. Large messages allocate exact buffers and require release by callers.

## Test Signals
`Proto2CodecTestBase` and `CodecTestUtil` patterns cover round trips. Tests should include invalid bytes, class cache reuse, direct/heap buffers, and leak checks.
