# sources/user-network-fs/nfs-ganesha/src/include/gsh_wait_queue.h

Purpose: This header defines a simple pthread-based wait queue building block.

Important APIs/types/functions: `wait_entry_t` combines a mutex and condition variable. Wait queue flags include `Wqe_LFlag_None`, `Wqe_LFlag_WaitSync`, and `Wqe_LFlag_SyncDone`. `wait_q_entry_t` tracks flags, waiter count, left/right wait entries, and an intrusive `glist_head`. Inline helpers initialize and destroy wait entries and queue entries.

Control flow: Callers embed or allocate a `wait_q_entry_t`, initialize its list node and condition variables, enqueue it via `glist`, and use the left/right wait entries for synchronization protocols implemented outside this header.

State and persistence: Queue state is in-memory: waiter counts, flags, two condition-variable endpoints, and queue membership. No persistent storage is involved.

Dependencies and integration points: Depends on pthreads, `gsh_list.h`, and `common_utils.h` for pthread wrapper macros. It is a utility for thread coordination elsewhere in the server.

Risks: The header only initializes primitives; it does not define locking rules. Destroying while waiters exist, failing to initialize `flags`/`waiters` explicitly, or list misuse can cause races or deadlocks.

Test signals: Test init/destroy paths, queue insertion/removal around initialized entries, wait/signal users for both left and right entries, flag transitions, and shutdown with no active waiters.
