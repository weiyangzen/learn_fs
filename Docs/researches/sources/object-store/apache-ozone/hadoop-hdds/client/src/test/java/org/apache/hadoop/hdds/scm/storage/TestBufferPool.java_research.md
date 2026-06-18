## sources/object-store/apache-ozone/hadoop-hdds/client/src/test/java/org/apache/hadoop/hdds/scm/storage/TestBufferPool.java

**Purpose:** Tests `BufferPool` allocation, reuse, release validation, capacity accounting, and blocking behavior under concurrent allocation pressure.

**Important APIs/types/functions:** `testBufferPool()` covers `BufferPool.empty()` and capacities/buffer sizes of `(1,1)`, `(3,1MiB)`, and `(10,1KiB)`. Helpers assert empty/full states, allocate up to capacity, fill buffers with random data to make identities distinguishable, release/reallocate the same instances, release in mixed order, and reject double releases. `testBufferPoolConcurrently()` fills a pool, verifies an allocator thread blocks and can be interrupted, then verifies a blocked allocator receives a released buffer once another thread releases it.

**Control flow:** Allocation loops grow the pool until capacity; when full, `allocateBuffer()` waits until release or interruption. Release transitions buffers from used to available, resets positions, and notifies waiters.

**State and persistence:** Tests in-memory pool state: capacity, buffer size, used count, total pool size, current buffer pointer, and buffer contents/positions. No persistence.

**Dependencies and integration points:** Depends on `ChunkBuffer`, `GenericTestUtils` log capture, SLF4J level control, AssertJ, and JUnit. It protects storage write buffering used by block output streams.

**Risks:** Thread coordination uses a spin/sleep loop on an `AtomicBoolean`, which is simple but time-sensitive on overloaded machines. Logging assertions couple tests to message text.

**Test signals:** Good unit signal for pool identity reuse, capacity invariants, and interruptible blocking. It does not test high-contention fairness or memory pressure beyond fixed capacities.
