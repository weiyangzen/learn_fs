# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/utils/db/Buffer.java

## Purpose
Internal reusable `CodecBuffer` holder for fetching variable-sized data from a `PutToByteBuffer` source, typically database direct-buffer reads.

## Important APIs, Types, And Functions
Package-private `Buffer` stores a mutable `CodecBuffer.Capacity`, an optional `PutToByteBuffer<RuntimeException> source`, and a cached `CodecBuffer`. Methods are `getFromDb()` and `release()`.

## Control Flow
`getFromDb()` prepares or allocates a direct resizable buffer. It invokes the source, returns null when the source is unavailable, returns the buffer when readable bytes match the required size, tries `setCapacity(required)`, and otherwise increases the shared capacity hint and reallocates.

## State And Persistence
State is an owned pooled direct buffer and adaptive initial-capacity hint. It must be released to return Netty memory to the pool. No disk persistence is owned here.

## Dependencies And Integration Points
Depends on `CodecBuffer`, `CodecBuffer.Capacity`, `PutToByteBuffer`, and Ratis `Preconditions`. It is a helper for DB APIs that can report required value size.

## Risks
Callers must not retain the buffer across `getFromDb()` reuse without ownership discipline. If `source` writes inconsistent sizes, assertions fail. Missing `release()` leaks pooled buffers.

## Test Signals
Tests should cover unavailable source, exact fit, capacity growth by `setCapacity`, reallocation growth, repeated reuse, and leak detection via `CodecBuffer.assertNoLeaks()`.
