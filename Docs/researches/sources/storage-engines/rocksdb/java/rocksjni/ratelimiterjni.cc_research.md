<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/ratelimiterjni.cc -->
# sources/storage-engines/rocksdb/java/rocksjni/ratelimiterjni.cc

Purpose: Bridges `org.rocksdb.RateLimiter` to C++ `ROCKSDB_NAMESPACE::RateLimiter`, giving Java code access to construction, disposal, rate updates, blocking requests, and counters.

Important APIs/types/functions: `Java_org_rocksdb_RateLimiter_newRateLimiterHandle` calls `NewGenericRateLimiter` and stores it in a heap `std::shared_ptr<RateLimiter>` handle. `disposeInternalJni` deletes the shared pointer wrapper. `setBytesPerSecond`, `getBytesPerSecond`, `request`, `getSingleBurstBytes`, `getTotalBytesThrough`, and `getTotalRequests` forward to the underlying C++ object. `RateLimiterModeJni::toCppRateLimiterMode` converts the Java enum byte.

Control flow: Java passes primitive configuration and a native handle. The constructor translates the mode, creates the C++ limiter, wraps it, and returns the wrapper address as `jlong`. All later calls reinterpret the handle, dereference the shared pointer, and call RocksDB.

State and persistence behavior: The file owns only native process memory. No disk state is written directly; persistence impact is indirect through throttling RocksDB IO. The Java wrapper must call dispose to release the shared pointer wrapper.

Dependencies and integration points: Includes generated JNI header `org_rocksdb_RateLimiter.h`, `rocksdb/rate_limiter.h`, conversion helpers, and `portal.h`. The handle can be shared with options/configuration objects that accept a rate limiter.

Risks: Handles are unchecked; a stale, zero, or wrong handle will crash or corrupt memory. `request` always uses `Env::IO_TOTAL`, so this binding does not expose a Java-side choice of IO priority/type. Counter values are returned as signed `jlong`, so very large unsigned C++ counters depend on Java-side interpretation.

Test signals: Useful tests create a limiter, verify get/set rate, issue small requests, observe counters increasing, verify mode/auto-tune construction, and ensure dispose is idempotently guarded by the Java owning object.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/ratelimiterjni.cc -->
