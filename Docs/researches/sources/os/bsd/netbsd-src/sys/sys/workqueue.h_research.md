# File Research: sources/os/bsd/netbsd-src/sys/sys/workqueue.h

Read completely: 61 lines.

Declares NetBSD's lightweight workqueue API for deferring small work items to thread context.

Core API:
- `struct work` is intentionally tiny so it can be embedded in other structures.
- `struct workqueue` is opaque.
- `workqueue_create` creates a queue with name, callback, callback argument, priority, IPL, and flags.
- `workqueue_destroy`, `workqueue_wait`, and `workqueue_enqueue` manage queue lifetime, wait for a work item, and enqueue work optionally targeted at a CPU.

Flags:
- `WQ_MPSAFE` marks callbacks as MP-safe.
- `WQ_PERCPU` requests per-CPU behavior.
- `WQ_FPU` indicates callbacks may use the FPU.

Risks and notes:
- Because `struct work` contains only a dummy pointer, callers must provide storage/lifetime discipline and avoid enqueueing the same work item unsafely.
