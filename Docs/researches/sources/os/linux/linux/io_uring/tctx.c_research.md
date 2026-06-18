# File Research: sources/os/linux/linux/io_uring/tctx.c

Task-context management for io_uring. This file binds rings to tasks, manages per-task io-wq offload, registered ring fds, task restrictions, and fork cleanup/clone behavior.

Key responsibilities:
- Allocates and frees `struct io_uring_task`.
- Creates per-task io-wq offload state and shared hash map.
- Installs/removes task-to-ring nodes in both task xarray and ctx task list.
- Tracks the last used ctx for fast submit-path lookup.
- Cleans task contexts on exit and drops io-wq when no rings remain.
- Registers and unregisters ring fds in per-task slots.
- Clones task-wide io_uring restrictions on fork.

Important data flows:
- `__io_uring_add_tctx_node()` lazily allocates task context, applies existing ctx io-wq worker limits, reactivates io-wq keepalive, then installs a ctx node.
- `io_uring_del_tctx_node()` removes xarray and ctx-list links, clears `last`, and marks io-wq exit-on-idle when no rings remain.
- Ringfd registration validates ring fds, stores `struct file *` refs in fixed task slots, and writes allocated offsets back to userspace.

Concurrency and locking:
- `ctx->uring_lock` protects hash-map allocation and some limit reads.
- `ctx->tctx_lock` protects `ctx->tctx_list`.
- Ringfd registration temporarily drops `ctx->uring_lock` while ensuring a tctx node exists.

Important invariants:
- Single-issuer rings reject submits from non-submitter tasks.
- Registered ring fds must refer to io_uring files.
- `__io_uring_free()` expects all ring nodes, io-wq, and cached refs to have already been cleaned.
