## sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/RateLimiterTest.java

### Purpose

`RateLimiterTest` validates basic Java binding behavior for RocksDB's native rate limiter.

### Important APIs, Types, And Functions

It uses the `RateLimiter` constructor, constants `DEFAULT_REFILL_PERIOD_MICROS`, `DEFAULT_FAIRNESS`, `DEFAULT_MODE`, `DEFAULT_AUTOTUNE`, `getBytesPerSecond`, `setBytesPerSecond`, `getSingleBurstBytes`, `getTotalBytesThrough`, and `getTotalRequests`.

### Control Flow

Each test constructs a rate limiter in a try-with-resources block, checks a getter, and closes it. The autotune test enables autotune and only asserts a positive byte-per-second value.

### State And Persistence Behavior

Rate limiter counters are runtime native object state only. No DB is opened, and no throttled IO is performed, so total bytes/requests remain zero.

### Dependencies And Integration Points

This integrates native rate limiter construction, Java constants, basic counters, mutable rate setting, and native handle closing.

### Risks And Edge Cases

- Single burst bytes are expected to be `100` for a 1000 B/s rate with default refill period; native default math changes would break the test.
- Autotune is smoke-tested but not exercised under load.
- Counters are not validated after actual requests.

### Test Signals

Signals are positive rates, single burst bytes of `100`, zero initial counters, and successful autotune construction. Static research only; no test command was run.
