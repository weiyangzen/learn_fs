# File Research: sources/os/linux/linux/io_uring/tctx.h

Header for task-context and registered-ring-fd helpers.

Key responsibilities:
- Defines `struct io_tctx_node`, linking a task and ring ctx.
- Declares task-context allocation, node add/remove, cleanup, and ringfd register/unregister helpers.
- Provides fast inline `io_uring_add_tctx_node()` using `current->io_uring->last`.

Important invariant:
- The fast path is valid only when the current task already has a tctx and its `last` ctx matches the submitted ring.
