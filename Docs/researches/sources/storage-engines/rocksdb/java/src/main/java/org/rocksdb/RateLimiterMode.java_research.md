# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/RateLimiterMode.java

## Purpose
`RateLimiterMode` is the Java enum mirror for native RocksDB rate-limiter mode selection. It determines whether the configured limiter charges reads, writes, or all I/O against the rate budget.

## Important APIs, Types, And Functions
- Enum constants: `READS_ONLY`, `WRITES_ONLY`, and `ALL_IO`.
- `getValue()` returns the byte code passed through JNI.
- `getRateLimiterMode(byte)` maps native byte values back to Java and throws for invalid values.

## Control Flow
`RateLimiter` constructors call `rateLimiterMode.getValue()` before creating the native limiter. JNI converts the byte through `RateLimiterModeJni::toCppRateLimiterMode`.

## State And Persistence Behavior
State is immutable enum metadata only. The selected mode becomes native rate-limiter configuration at construction time; changing the mode after construction is not supported by this Java wrapper.

## Dependencies And Integration Points
- Used by `RateLimiter` full constructors and default `RateLimiter.DEFAULT_MODE`.
- JNI conversion is implemented through portal conversion helpers included by `ratelimiterjni.cc`.
- Native tests iterate C++ modes for read/write accounting behavior; the Java enum values must match that native ordering.

## Risks And Edge Cases
- Byte-value drift from native `RateLimiter::Mode` would silently configure the wrong limiting behavior.
- Java API exposes no null guard in `RateLimiter` full constructor; passing null for `rateLimiterMode` results in a Java `NullPointerException`.
- The Javadoc return text says "AccessHint instance", which is a copy/paste documentation error.

## Test Signals
- Native mode tests verify expected C++ semantics.
- Java should have a focused enum/JNI test asserting each Java byte maps to the intended native mode through a constructed limiter, especially because wrong mode selection can be hard to detect in normal options tests.
