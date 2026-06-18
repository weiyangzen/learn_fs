# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/ByteStringConversion.java

## Purpose
Provides a configurable conversion strategy from `ByteBuffer` to Ratis-shaded protobuf `ByteString`, selecting safe copying or unsafe wrapping based on Ozone configuration.

## Important APIs, Types, And Functions
`createByteBufferConversion(boolean unsafeEnabled)` returns either `UnsafeByteOperations::unsafeWrap` or `ByteStringConversion::safeWrap`. `safeWrap(ByteBuffer)` copies bytes with `ByteString.copyFrom(buffer)`, then flips the buffer.

## Control Flow
Callers create a reusable `Function<ByteBuffer, ByteString>` at configuration time, then apply it when constructing protobuf messages.

## State And Persistence
The class is stateless. It affects memory ownership: safe mode copies data, while unsafe mode shares the buffer with the resulting `ByteString`.

## Dependencies And Integration Points
References `OzoneConfigKeys.OZONE_UNSAFEBYTEOPERATIONS_ENABLED`, Ratis-shaded `ByteString`, and `UnsafeByteOperations`. It is relevant to container and pipeline RPC serialization paths.

## Risks And Test Signals
Unsafe wrapping can expose mutable-buffer corruption if callers reuse buffers before protobuf consumption. `safeWrap` flips the buffer after copy, which is an unusual side effect. Tests should cover buffer position/limit behavior and corruption resistance with unsafe enabled/disabled.
