# sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/hdds/scm/storage/ByteArrayReader.java

## Purpose
`ByteArrayReader` adapts the generic `ByteReaderStrategy` interface to Java byte-array reads. It lets stream implementations share read-loop logic across `read(byte[], int, int)` and `read(ByteBuffer)`.

## Important APIs and Types
The constructor validates byte array, offset, and length. `readFromBlock(InputStream, int)` delegates to `InputStream.read(byte[], offset, numBytesToRead)`, advances its offset, reduces target length, and returns bytes read. `getTargetLength()` exposes remaining desired bytes.

## Control Flow
Higher-level streams pass this strategy into `ExtendedInputStream.read(ByteReaderStrategy)`. Each successful delegated read mutates the strategy so the next loop iteration appends data to the next byte-array position.

## State and Persistence Behavior
It stores only the target array reference, mutable offset, and mutable target length. It does not own buffers and performs no persistence.

## Dependencies and Integration Points
Used by `ExtendedInputStream.read(byte[], int, int)`, `BlockInputStream`, `MultipartInputStream`, and EC readers through the shared strategy interface.

## Risks
The method subtracts `numBytesRead` without handling `-1`; callers in this code generally avoid delegating when EOF is expected and verify exact reads, but this strategy is not defensive if used directly with an EOF-producing stream. Array-backed ownership remains with the caller.

## Test Signals
Coverage is mostly indirect through stream tests such as `TestBlockInputStream`, `TestECBlockInputStream`, and multipart/key stream tests.
