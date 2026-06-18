# sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/io/KeyOutputStreamSemaphore.java

Purpose: This helper encapsulates optional per-key write concurrency limiting for `KeyOutputStream`.

Important APIs and types: The constructor accepts `maxConcurrentWritePerKey`; `acquire`, `release`, and `getQueueLength` wrap a Java `Semaphore`.

Control flow: Positive concurrency creates a semaphore with that many permits. Zero is rejected as invalid configuration. Negative values disable limiting by leaving the semaphore null. `acquire` blocks until a permit is available and converts interruption into `InterruptedIOException` while restoring the interrupt flag; `release` is a no-op when disabled.

State and persistence behavior: Runtime state is only the semaphore and its queued/acquired permits. It has no persistence.

Dependencies and integration points: Used by `KeyOutputStream.write`, `flush`, and `hsync` to bound concurrent operations per key. It logs trace-level acquire/release events.

Risks: Callers must release in `finally` to avoid permit leaks. Negative values completely disable concurrency control, so configuration semantics must be intentional. The constructor is package-private, limiting direct external validation.

Test signals: Tests should cover positive permit blocking/queue length, zero rejecting config, negative no-op behavior, interruption converting to `InterruptedIOException`, and release not throwing when disabled.
