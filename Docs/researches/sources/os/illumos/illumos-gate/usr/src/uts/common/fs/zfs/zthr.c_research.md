# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/zthr.c

This file implements the ZFS zthr infrastructure: a small managed kernel-thread abstraction for SPA-scoped background work that may span multiple transaction groups. It is intended for operations with a durable or in-memory “work needed/running/stopped” indicator, where external threads start work and the zthr itself is responsible for deciding when the work is complete.

The central state is `struct zthr`, containing the current `kthread_t`, state and request mutexes, a condition variable, a cancellation flag, an optional maximum sleep interval, and consumer-provided `checkfunc`, `func`, and argument pointer. `zthr_create()` delegates to `zthr_create_timer()`, which initializes this state and starts `zthr_procedure()` at system priority.

`zthr_procedure()` holds `zthr_state_lock` while checking cancellation and invoking the checker. If the checker returns true, it drops the state lock while running the worker callback so cancellation can be observed between callback invocations or explicitly via `zthr_iscancelled()`. If no work is needed, it sleeps either indefinitely on `zthr_cv` or with `cv_timedwait_hires()` according to `zthr_wait_time`. On cancellation, it clears the thread pointer and cancellation flag, broadcasts to wake the canceling requester, and exits.

External operations are serialized by `zthr_request_lock` and then use `zthr_state_lock` for state transitions. `zthr_wakeup()` broadcasts without changing state. `zthr_cancel()` sets `zthr_cancel`, wakes a sleeping thread, and waits until `zthr_thread` becomes `NULL`. `zthr_resume()` recreates the kernel thread if it is currently canceled/stopped. `zthr_destroy()` asserts the thread has already stopped, destroys synchronization primitives, and frees the object.

The main correctness contract is lock ordering and cancellation visibility. Normal request paths take request lock before state lock, while `zthr_iscancelled()` intentionally takes only the state lock because it is called by the zthr callback itself and must not deadlock with a concurrent cancel request.
