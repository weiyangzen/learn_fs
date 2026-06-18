# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/RateLimiter.java

## Purpose
`RateLimiter` is the Java owning wrapper for RocksDB's generic native rate limiter. It controls background I/O throughput, especially flush and compaction writes by default, and can be installed into `Options` or `DBOptions`.

## Important APIs, Types, And Functions
- Defaults: refill period `100000` microseconds, fairness `10`, mode `WRITES_ONLY`, and auto-tune disabled.
- Overloaded constructors funnel into the full constructor accepting `rateBytesPerSecond`, `refillPeriodMicros`, `fairness`, `RateLimiterMode`, and `autoTune`.
- `setBytesPerSecond(long)` dynamically changes the native limit.
- `getBytesPerSecond()`, `getSingleBurstBytes()`, `getTotalBytesThrough()`, and `getTotalRequests()` expose native counters/configuration.
- `request(long)` synchronously requests tokens and blocks if the native limiter cannot satisfy the request.
- `disposeInternal(long)` deletes the native `std::shared_ptr<RateLimiter>` wrapper.

## Control Flow
Construction calls the JNI `newRateLimiterHandle`, which converts `RateLimiterMode` to C++ and allocates a `std::shared_ptr<rocksdb::RateLimiter>` containing `NewGenericRateLimiter(...)`. Public methods assert ownership via `isOwningHandle()` and then dispatch through JNI to native methods. `request(long)` maps to native `Request(bytes, Env::IO_TOTAL)`, so Java cannot select per-request operation type.

## State And Persistence Behavior
The Java object owns a native heap allocation containing a shared pointer to the actual native limiter. Installing it in `Options` or `DBOptions` stores the native shared limiter in RocksDB options and Java fields such as `rateLimiter_` retain the Java object to keep the native handle alive. Counters and token state live entirely in native code. The object must be closed/disposed to release the Java-side shared-pointer allocation.

## Dependencies And Integration Points
- Extends `RocksObject` for native-handle ownership and disposal.
- Depends on `RateLimiterMode` for native mode bytes.
- JNI implementation is in `java/rocksjni/ratelimiterjni.cc` and uses `rocksdb/rate_limiter.h`, `NewGenericRateLimiter`, and `RateLimiterModeJni`.
- `Options.setRateLimiter` and `DBOptions.setRateLimiter` pass the handle into native options and retain the Java reference.
- C++ `util/rate_limiter_test.cc` covers core native behavior including modes, fairness, rate changes, pending requests, and auto-tune.

## Risks And Edge Cases
- Java constructors do not validate positive rates or fairness; invalid values rely on native assertions/errors.
- `request(bytes)` can block the caller, so using it on latency-sensitive Java threads can deadlock or stall if configured too low.
- Callers must ensure requested bytes are below `getSingleBurstBytes()` as documented; Java does not enforce it.
- Because Java `request` uses `Env::IO_TOTAL`, it is less expressive than C++ APIs that distinguish read/write operation types.
- Disposal while options or DBs still refer to the limiter is risky unless shared ownership has already been transferred correctly.

## Test Signals
- Java `OptionsTest` verifies rate limiter assignment and option copying.
- `RocksDBSample` demonstrates creating and installing a `RateLimiter`.
- Native C++ tests provide the strongest behavioral coverage for limiter modes, accounting, blocking, and auto-tuning. Java-specific tests should additionally verify JNI getters/setters and lifecycle interactions with `Options`/`DBOptions`.
