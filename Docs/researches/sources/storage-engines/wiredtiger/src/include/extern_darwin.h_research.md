## sources/storage-engines/wiredtiger/src/include/extern_darwin.h

Purpose: this generated platform prototype header declares the Darwin-specific synchronization functions used by WiredTiger. It keeps macOS semaphore and futex-like APIs separate from the general POSIX and core `extern.h` surface.

Important APIs/types/functions: `__wt_futex_wait` waits on a `volatile WT_FUTEX_WORD *` while it equals an expected value, accepts a microsecond timeout, and can return the observed wake value through `wake_valp`. `__wt_futex_wake` wakes either one or all waiters according to `WT_FUTEX_WAKE` and publishes a wake value. `__wt_semaphore_init`, `__wt_semaphore_destroy`, `__wt_semaphore_post`, and `__wt_semaphore_wait` wrap `WT_SEMAPHORE` lifecycle and counting behavior for Darwin. All return `int` and are marked `warn_unused_result`.

Control flow: higher-level lock, condition, and thread coordination code calls these declarations through WiredTiger's internal synchronization abstractions. Wait paths typically validate the current futex word, sleep with a bounded timeout or until woken, then re-check shared state in the caller. Semaphore paths follow explicit init/post/wait/destroy lifecycle.

State and persistence behavior: no durable state is managed. The state is process-local synchronization state in `WT_FUTEX_WORD` and `WT_SEMAPHORE`; mistakes affect liveness, wakeup ordering, and shutdown rather than on-disk data directly. Because these primitives guard cache, eviction, checkpoint, and connection state, synchronization bugs can indirectly cause inconsistent in-memory decisions before persistence.

Dependencies and integration points: it depends on `futex.h` for `WT_FUTEX_WORD` and `WT_FUTEX_WAKE`, `WT_SESSION_IMPL`, `WT_SEMAPHORE`, `time_t`, and the Darwin implementation files selected by the build. It integrates with thread groups, condition variables, eviction/checkpoint workers, and any subsystem using WiredTiger semaphores.

Risks: Darwin does not expose Linux futex semantics directly, so implementation details must faithfully emulate the expected compare/sleep/wake behavior and timeout units. Lost wakeups, mishandled wake values, or unchecked return values can deadlock worker threads. Semaphore destroy during active waiters and timeout granularity differences are important edge cases.

Test signals: macOS builds, concurrency stress tests, eviction/checkpoint worker lifecycle tests, forced shutdown tests with waiting threads, timeout behavior tests, and sanitizer/thread-sanitizer runs are the best signals.
