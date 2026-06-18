# File Research: sources/os/bsd/netbsd-src/sys/sys/threadpool.h

Read completely: 85 lines.

Declares NetBSD kernel threadpool and per-CPU threadpool interfaces.

Key elements:
- Kernel-only header.
- Opaque pool types include `threadpool`, `threadpool_percpu`, and `threadpool_thread`.
- `struct threadpool_job` contains caller lock, current worker thread pointer, queue link, refcount, condition variable, job callback, and fixed job name.
- APIs initialize global threadpools, acquire/release shared pools by priority, and acquire/release per-CPU pools.
- Per-CPU pool refs can be local or remote by `cpu_info`.
- Job APIs initialize/destroy/mark done, schedule jobs, cancel synchronously, and cancel asynchronously.

Risks and notes:
- Job lifetime depends on refcount, lock, condition variable, and cancellation semantics.
- Callers must use the right pool priority and respect job lock ownership.
