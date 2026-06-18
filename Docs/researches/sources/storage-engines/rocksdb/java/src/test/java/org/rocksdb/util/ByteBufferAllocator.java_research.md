# sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/util/ByteBufferAllocator.java

Purpose: Small test utility interface abstracting heap versus direct `ByteBuffer` allocation.

Important APIs/types/functions: `ByteBufferAllocator.allocate(int capacity)`, constants `HEAP` and `DIRECT`.

Control flow and state: callers select one of two singleton allocator implementations. Each call returns a fresh `ByteBuffer` of the requested capacity.

State and persistence behavior: stateless; returned buffers are transient test objects.

Dependencies and integration points: used by RocksJava tests that must exercise both direct JNI buffer paths and ordinary heap buffers without duplicating test bodies.

Risks: no validation of capacity; direct buffer allocation can pressure off-heap memory in large tests.

Test signals: indirect coverage through `WriteBatchWithIndexTest` and comparator tests using direct/heap pathways.
