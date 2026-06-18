## sources/object-store/apache-ozone/hadoop-hdds/client/src/test/java/org/apache/hadoop/ozone/client/io/TestBoundedElasticByteBufferPool.java

**Purpose:** Tests `BoundedElasticByteBufferPool` FIFO reuse and maximum cached byte-size enforcement.

**Important APIs/types/functions:** `testLogicalTimestampOrdering()` puts three same-size buffers, records identity hash codes, retrieves three buffers of the same size, and asserts FIFO identity order plus zero pool size afterward. `testPoolBoundingLogic()` creates a 3 MiB pool, stores 2 MiB and 1 MiB buffers to exactly fill it, verifies a subsequent 3 MiB buffer is rejected, retrieves the first two by identity, and confirms a later 3 MiB request allocates a new instance rather than returning the rejected buffer.

**Control flow:** `putBuffer()` accepts a buffer only if `currentPoolSize + capacity <= maxPoolSize`; `getBuffer()` removes a matching cached buffer or allocates a new one. Ordering is driven by logical timestamps/FIFO behavior.

**State and persistence:** Tests in-memory cached buffer state and the exposed `currentPoolSize`. No persistence.

**Dependencies and integration points:** Depends on Java `ByteBuffer` and JUnit. Integrates with EC reconstructed stream buffer pooling where unbounded elastic pooling would otherwise retain excessive memory.

**Risks:** Identity hash code comparison is a proxy for object identity; `assertSame` would be more direct. Tests cover heap buffers only and do not cover direct buffers or mixed size ordering beyond the chosen cases.

**Test signals:** Good signal for memory bounding and stable FIFO reuse behavior.
