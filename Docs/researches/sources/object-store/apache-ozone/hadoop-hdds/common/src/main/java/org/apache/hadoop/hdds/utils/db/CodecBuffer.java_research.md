# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/utils/db/CodecBuffer.java

## Purpose
Wraps Netty `ByteBuf` as an Ozone codec buffer for pooled heap/direct memory, direct RocksDB-style byte access, protobuf IO, and leak diagnostics.

## Important APIs, Types, And Functions
Important pieces are `Allocator` direct/heap factories, `Capacity`, `allocateDirect`, `allocateHeap`, `wrap(byte[])`, `wrap(ByteString)`, `enableLeakDetection`, `assertNoLeaks`, `release`, `asWritableByteBuffer`, `asReadOnlyByteBuffer`, `getArray`, `startsWith`, `getInputStream`, numeric `put*`, `put(ByteBuffer)`, `put(OutputStream source)`, and package-private `putFromSource`.

## Control Flow
Allocation uses Netty pooled allocators; non-negative capacity fixes max capacity, negative capacity allows growth. `release()` completes a future and releases the underlying buffer. Encoding helpers update writer indexes after source functions write to `ByteBuffer` or `OutputStream`. Leak detection swaps the factory to a subclass whose finalizer calls `detectLeaks`.

## State And Persistence
State is pooled buffer reference count, wrapped source object, captured allocation stack, and release future. No persistent storage is owned, but bytes represent persistent codec data.

## Dependencies And Integration Points
Depends on Ratis-shaded Netty buffers, protobuf `ByteString`, Ratis utilities, Hadoop `StringUtils`, and codec implementations. It is central to DB direct-buffer pathways.

## Risks
Manual release is required for non-empty buffers. `getArray()` consumes readable bytes by advancing the reader index. `asWritableByteBuffer()` exposes max capacity, so writers must respect writer-index handling. Leak detection uses finalization and carries performance cost.

## Test Signals
`CodecTestUtil`, `TestLeakDetector`, and consumers such as multipart key codec tests cover round trips and leaks. Additional tests should cover direct vs heap, zero-capacity release idempotency, `startsWith`, and source-size mismatch behavior.
