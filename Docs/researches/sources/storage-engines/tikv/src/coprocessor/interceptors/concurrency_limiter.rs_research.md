# sources/storage-engines/tikv/src/coprocessor/interceptors/concurrency_limiter.rs

Purpose: provides a future wrapper that lets light coprocessor tasks run without taking a semaphore, while forcing heavier tasks to acquire a permit after a configured execution-time threshold.

Important APIs/types: `limit_concurrency(fut, semaphore, time_limit_without_permit)` constructs `ConcurrencyLimiter`. The internal state machine has `NotLimited`, `Acquiring(Instant)`, and `Acquired { _permit }`. Its `Future::poll` tracks elapsed time across pending polls; once elapsed time exceeds the threshold, it polls semaphore acquisition before continuing the wrapped future.

State and metrics: state is per future. Metrics increment unacquired/acquired counters, waiting gauge, and semaphore wait histogram. No persistent state exists. Dependencies are `tokio::sync::Semaphore`, `pin_project`, `futures::FutureExt`, and coprocessor metrics.

Integration points: unary endpoint handling wraps request execution with `limit_concurrency` when a Yatp-backed endpoint has a semaphore. Streaming takes a permit up front instead. Risks include undercounting CPU-heavy futures that do not yield, because elapsed execution is observed only around polls, and fairness depending on semaphore order. Tests verify light tasks complete without permits and heavy tasks serialize behind semaphore acquisition.
