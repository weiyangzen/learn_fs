# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/keyvalue/impl/TestMappedBufferManager.java

## Purpose
This test verifies the caching semantics of `MappedBufferManager.computeIfAbsent`. It ensures a buffer already cached for a file/position/size key is reused instead of replaced by a later supplier.

## Important APIs, types, and functions
The file constructs `MappedBufferManager(100)` and calls `computeIfAbsent(file, position, size, supplier)`. It uses `ByteBuffer.allocate` for two different candidate buffers and JUnit `assertEquals`.

## Control flow
The first call stores `buffer1` for a path, position zero, and size 1024. The second call uses an equivalent path string, same position and size, but a supplier for `buffer2` of a different capacity. The expected return is still `buffer1`.

## State and persistence behavior
The state under test is the manager's in-memory mapping from file/position/size to `ByteBuffer`. No filesystem access is performed even though the key looks like a real chunk file path.

## Dependencies and integration points
`MappedBufferManager` is used by chunk read utilities for memory-mapped or cached buffers. This test protects cache-key behavior relied on by repeated reads of the same chunk range.

## Risks and edge cases
The main risk is replacing a cached buffer on a repeated lookup, which could defeat reuse and increase memory churn. It also implicitly checks that identical file strings are treated as identical keys.

## Test signals
The single signal is object equality: both `computeIfAbsent` calls return the original `buffer1`.
