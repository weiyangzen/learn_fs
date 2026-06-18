## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/keyvalue/impl/MappedBufferManager.java

Purpose: Manages a process-wide cache of memory-mapped read buffers while bounding the number of active mappings through a semaphore quota.

Important APIs and functions: The constructor sets quota capacity and a striped lock table. `getQuota()` attempts to acquire permits and launches asynchronous cleanup of cleared weak references when quota is exhausted. `releaseQuota()` returns permits. `availableQuota()` exposes current permits. `computeIfAbsent()` locks by file/position/size key, returns a live cached buffer or installs a newly supplied buffer.

Control flow and state: `mappedBuffers` is static and maps string keys to weak references, so mappings can be reused across manager instances but reclaimed by GC. `cleanupInProgress` prevents concurrent cleanup passes. `Striped.lazyWeakLock(1024)` serializes one cache key without global locking.

Persistence and dependencies: No direct persistence occurs, but cached `ByteBuffer` instances typically wrap memory-mapped file regions used by chunk reads. It depends on Guava `Striped`, Java weak references, `ConcurrentHashMap`, `Semaphore`, and `CompletableFuture`.

Risks: Quota is optimistic: callers must acquire before compute, and a cache hit releases one permit because no new mapping was consumed. Incorrect caller ordering can leak or over-release permits. Static cache state crosses container/file lifetimes. Async cleanup is best-effort and does not force unmapping. Key construction by string concatenation must remain collision-free for file names, positions, and sizes.

Test signals: Exercise quota acquisition/failure, cached hit permit release, weak-reference cleanup permit restoration, concurrent `computeIfAbsent()` for the same key, concurrent different-key access, null supplier result, and manager reuse across files.
