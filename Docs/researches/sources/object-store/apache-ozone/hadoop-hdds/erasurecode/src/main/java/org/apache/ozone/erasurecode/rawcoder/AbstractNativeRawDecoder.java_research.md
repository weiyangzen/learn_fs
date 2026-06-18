<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/AbstractNativeRawDecoder.java -->
# sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/AbstractNativeRawDecoder.java

## Purpose
`AbstractNativeRawDecoder` is the shared base for native raw decoders. It adapts Ozone's `RawErasureDecoder` state objects to the Hadoop native erasure-code accessor shape and enforces read-lock protection around native decoder state.

## Important APIs, Types, and Functions
The class extends `RawErasureDecoder`, owns a protected `ReentrantReadWriteLock decoderLock`, implements `doDecode(ByteBufferDecodingState)` and `doDecode(ByteArrayDecodingState)`, declares `performDecodeImpl(...)`, and returns `true` from `preferDirectBuffer()`.

## Control Flow
The direct-buffer path records input and output positions into offset arrays, acquires `decoderLock.readLock()`, calls subclass `performDecodeImpl` with buffers, offsets, decode length, erased indexes, and outputs, then releases the lock. The byte-array path logs a `PerformanceAdvisory`, converts byte arrays into direct buffers, delegates to the ByteBuffer path, and copies direct output bytes back into caller arrays.

## State and Persistence Behavior
Persistent state is the lock; native coder state is held by subclasses. There is no disk persistence. The lock protects native structures against concurrent release and decode, although only read-side locking is in this base.

## Dependencies and Integration Points
It depends on `ECReplicationConfig`, `ByteBufferDecodingState`, `ByteArrayDecodingState`, Hadoop `PerformanceAdvisory`, and subclass implementations such as `NativeRSRawDecoder` and `NativeXORRawDecoder`.

## Risks and Test Signals
Risks include copy-back mistakes in byte-array conversion, direct buffer allocation overhead, native release races if subclasses do not use the write lock, and offset/position mismatch with Hadoop native accessors. Tests should cover direct and heap inputs, sliced buffers, decode after release, native fallback behavior, and concurrent release/decode stress where available.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/AbstractNativeRawDecoder.java -->
