## sources/user-network-fs/libtirpc/src/clnt_fd_locks.h

Purpose: Provides inline support for per-file-descriptor client locks shared by datagram and virtual-circuit transports, ensuring multiple `CLIENT` handles over the same fd do not concurrently read/write interleaved RPC records.

Important APIs and control flow: Defines `fd_lock_t` with `active`, `pending`, and condition variable fields. Without `MAX_FDLOCKS_PREALLOC`, `fd_locks_t` is a TAILQ of `fd_lock_item_t` nodes keyed by fd and refcounted. With preallocation, low-numbered fds are mapped into an array sized by `__rpc_dtbsize` and `MAX_FDLOCKS_PREALLOC`; higher fds still use the TAILQ. `fd_locks_init`, `fd_locks_destroy`, `fd_lock_create`, and `fd_lock_destroy` allocate, reuse, refcount, and clean up locks.

State and persistence: The header owns no global instance; each transport has its own static `fd_locks_t *`. Lock state persists for the lifetime of active client handles.

Dependencies and integration: Requires callers to hold the global `clnt_fd_lock` around create/destroy and active/pending changes.

Risks and test signals: Preallocated locks do not increment refs and may outlive individual clients. TAILQ destroy uses `TAILQ_FOREACH` while freeing, which is sensitive to implementation. Tests should cover shared fd refcounts, high fd allocation, pending wait/cleanup, and preallocation boundary behavior.
