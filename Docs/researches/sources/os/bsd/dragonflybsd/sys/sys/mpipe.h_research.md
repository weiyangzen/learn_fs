# File Research: sources/os/bsd/dragonflybsd/sys/sys/mpipe.h

Kernel-only pipelined fixed-size allocation facility with optional persistent cached object state.

Key responsibilities:
- Defines `struct malloc_pipe`, which manages a bounded cache/array of fixed-size allocations with an LWKT token and callback queue.
- Exposes `mpipe_init`, `mpipe_done`, waitable/non-waitable allocation, callback allocation, wait, and free APIs.
- Supports constructor and deconstructor hooks plus caller-private data.
- Defines flags controlling zeroing, cached data lifetime, interrupt reserve use, queue waiting, callback mode, and teardown.

Important behavior:
- Intended to allow blocking allocations while avoiding allocation deadlocks by maintaining a preallocated nominal pool.
- New buffers are zeroed by default.
- `MPF_CACHEDATA` preserves reused buffer contents and delays deconstruction until physical free.
- `MPF_NOZERO` disables zeroing for newly allocated buffers and cache reuses.

Dependencies:
- Kernel-only; rejects userland inclusion.
- Includes `_malloc.h`, `thread.h`, and `queue.h`.
- Uses `malloc_type_t`, `struct lwkt_token`, `struct thread`, and `STAILQ`.

Notable risks:
- Cached-data mode requires callers to tolerate stale contents.
- Callback allocations imply asynchronous control flow and valid callback arguments until completion.
- Pool sizing fields (`ary_count`, `max_count`, `free_count`, `total_count`) are correctness-critical for deadlock avoidance.
