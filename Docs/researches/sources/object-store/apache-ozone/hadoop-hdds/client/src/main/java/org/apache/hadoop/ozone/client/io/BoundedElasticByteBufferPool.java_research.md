# sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/ozone/client/io/BoundedElasticByteBufferPool.java

## Purpose
`BoundedElasticByteBufferPool` is a bounded implementation of Hadoop `ByteBufferPool`. It reuses heap and direct buffers while capping total cached buffer capacity to avoid unbounded memory growth in long-lived clients such as S3 Gateway.

## Important APIs and Types
`getBuffer(boolean, int)` retrieves the smallest cached buffer with capacity at least the requested length or allocates a new buffer. `putBuffer(ByteBuffer)` clears and caches a returned buffer only if doing so would not exceed `maxPoolSize`. `getCurrentPoolSize()` is visible for tests. Internal `Key` sorts buffers by capacity then logical insertion timestamp.

## Control Flow
Two `TreeMap<Key, ByteBuffer>` instances separate heap and direct buffers. A synchronized `getBuffer` uses `ceilingEntry(new Key(length, 0))`, removes the selected buffer, decrements current pool size, clears it, and returns it. `putBuffer` rejects nulls and over-budget returns, then stores the buffer with a unique logical timestamp and increments current size.

## State and Persistence Behavior
State is in-memory buffer maps, max pool size, current cached capacity counter, and logical timestamp. No persistence occurs.

## Dependencies and Integration Points
Can be supplied to `BlockInputStreamFactoryImpl` and EC reconstruction streams through the `ByteBufferPool` interface. Uses Guava `ComparisonChain` and Apache Commons `HashCodeBuilder`.

## Risks
The pool accounts cached buffer capacity, not outstanding allocated buffers. Very large returned buffers may be dropped, which is intended but can increase allocation churn. All operations are synchronized; high-concurrency read reconstruction could contend on this pool.

## Test Signals
`TestBoundedElasticByteBufferPool` covers buffer reuse, direct/heap separation, max-size enforcement, and size accounting.
