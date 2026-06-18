# sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/util/HeapByteBufferAllocator.java

Purpose: `ByteBufferAllocator` implementation returning array-backed heap buffers for non-direct JNI path testing.

Important APIs/types/functions: `allocate(int capacity)` delegates to `ByteBuffer.allocate`.

Control flow and state: stateless allocation on demand.

State and persistence behavior: heap buffers are ordinary GC-managed Java objects.

Dependencies and integration points: selected through `ByteBufferAllocator.HEAP` in tests that compare heap and direct buffer API behavior.

Risks: array-backed buffers can take different JNI paths from direct buffers, so this helper should be paired with direct tests rather than treated as complete coverage.

Test signals: indirect coverage through buffer-parameterized tests.
