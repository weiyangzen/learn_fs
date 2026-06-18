# File Research: sources/local-fs/squashfs-tools/squashfs-tools/thread.c

This file tracks active block and fragment deflator threads and enforces an overcommit limit for fragment work.

Key globals:
- `thread_mutex`: exported mutex protecting thread accounting.
- `idle`: condition variable signaled when a thread becomes idle.
- Static `threads` array, current index, active fragment/block counters, waiter count, and overcommit count.

Key functions:
- `set_overcommit`: computes extra allowed active threads from processor count and percent.
- `get_thread_id`: lazily allocates `processors * 2` thread records, assigns type/state, and increments active counters.
- `set_thread_idle`: decrements active counters, marks idle, and signals a waiter.
- `wait_thread_idle`: throttles fragment threads while total active threads exceeds `processors + overcommit`.
- `dump_threads`: prints active fragment/block thread ids.

Important behavior:
- Block threads are reactivated directly if idle.
- Fragment threads may sleep on `idle` while over the active-thread budget.
- The code assumes callers hold the relevant queue mutex when calling `wait_thread_idle`; comments state it is called with the thread mutex held, but the function waits on the passed queue mutex.

Concurrency-sensitive details:
- `pthread_cleanup_push/pop` protects `get_thread_id` and `dump_threads` mutex unlocks on cancellation.
- The fixed allocation size assumes exactly two thread classes with up to `processors` threads each.
