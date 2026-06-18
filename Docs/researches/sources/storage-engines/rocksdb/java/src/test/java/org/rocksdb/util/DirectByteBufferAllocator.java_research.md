# sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/util/DirectByteBufferAllocator.java

Purpose: `ByteBufferAllocator` implementation returning direct off-heap buffers for JNI path testing.

Important APIs/types/functions: `allocate(int capacity)` delegates to `ByteBuffer.allocateDirect`.

Control flow and state: stateless allocation on demand.

State and persistence behavior: no persistence; allocated direct buffers are released by JVM cleaner/GC.

Dependencies and integration points: selected through `ByteBufferAllocator.DIRECT` in tests that verify RocksJava APIs accept and advance direct buffers correctly.

Risks: direct buffers consume off-heap memory and are not reclaimed immediately; excessive use in tests can expose memory pressure.

Test signals: coverage comes from tests parameterized over direct allocation.
