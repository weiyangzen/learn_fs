# File Research: sources/os/linux/linux-stable/fs/ocfs2/localalloc.h

Purpose: declares the OCFS2 local allocation lifecycle, recovery, sizing, allocation, free, and enable-worker APIs.

Read coverage: complete file read, 52 lines.

Declared APIs:
- Lifecycle/sizing: `ocfs2_load_local_alloc()`, `ocfs2_shutdown_local_alloc()`, `ocfs2_la_set_sizes()`, `ocfs2_la_default_mb()`.
- Recovery: `ocfs2_begin_local_alloc_recovery()`, `ocfs2_complete_local_alloc_recovery()`.
- Allocation decision and operations: `ocfs2_alloc_should_use_local()`, `ocfs2_reserve_local_alloc_bits()`, `ocfs2_claim_local_alloc_bits()`, `ocfs2_free_local_alloc_bits()`.
- Feedback/worker: `ocfs2_local_alloc_seen_free_bits()`, `ocfs2_la_enable_worker()`.

Important dependencies:
- Uses `struct ocfs2_super`, `struct ocfs2_dinode`, `struct ocfs2_alloc_context`, JBD2 `handle_t`, and workqueue types.

Concurrency and lifetime:
- Header exposes allocation-context based ownership: reserve fills an `ocfs2_alloc_context`, claim/free consume it under a transaction.
- Recovery APIs transfer ownership of an allocated dinode copy to the caller/completion path.

Risk and edge cases:
- Callers must not use local allocation merely because it is compiled in; `ocfs2_alloc_should_use_local()` enforces state and size policy.
- Claim/free require a matching local allocation context and active journal handle.
