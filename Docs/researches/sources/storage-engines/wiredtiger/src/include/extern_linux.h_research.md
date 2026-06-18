## sources/storage-engines/wiredtiger/src/include/extern_linux.h

Purpose: this generated platform prototype header declares the Linux-specific futex and semaphore entry points used by WiredTiger synchronization code.

Important APIs/types/functions: the futex declarations mirror the Darwin surface: `__wt_futex_wait` blocks on a 32-bit `WT_FUTEX_WORD` if the observed value matches `expected`, with timeout and optional wake-value reporting, while `__wt_futex_wake` wakes one or all waiters and writes a wake value. The semaphore declarations provide `WT_SEMAPHORE` init, destroy, post, and wait. All functions return status and carry `warn_unused_result`.

Control flow: low-level Linux synchronization implementations back higher-level condition variables, semaphores, and thread coordination. Callers are expected to update shared words atomically, use futex wait as a blocking slow path, and wake waiters after publishing the state change they should observe.

State and persistence behavior: the only state is in-memory synchronization state. Linux futex operations are tied to the 32-bit word documented in `futex.h`; no file or metadata state is persisted. Correctness still affects persistence indirectly because these primitives coordinate threads that flush, checkpoint, evict, and close data handles.

Dependencies and integration points: it depends on Linux system futex support through implementation files, `WT_FUTEX_WORD`, `WT_FUTEX_WAKE`, `WT_SEMAPHORE`, `WT_SESSION_IMPL`, and `time_t`. It integrates with the same engine-wide synchronization paths as Darwin and Windows but can use native futex semantics.

Risks: futex correctness requires exact word sizing, expected-value comparison, timeout conversion, EINTR/retry behavior, and memory ordering around wait/wake. Returning wake values through `wake_valp` means stale or racy publication would confuse higher layers. Callers must not ignore errors from these functions.

Test signals: Linux concurrency stress, thread sanitizer builds where available, futex timeout and wake-one/wake-all tests, worker shutdown tests, and long-running eviction/checkpoint/backup workloads are relevant.
