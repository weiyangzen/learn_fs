# File Research: sources/local-fs/dlm/dlm_controld/plock.c

This file implements user-space coordination of DLM POSIX locks (`plocks`) through `/dev/misc/dlm_plock` and cluster messages. It tracks byte-range locks per resource, waiters, optional resource ownership, saved messages during joins, checkpoint-style state transfer, and purge/drop behavior.

Core data structures:
- `struct resource`: one lock resource by number, with owner state, flags, last access time, lists of locks/waiters/pending ops, and an rb-tree node.
- `struct posix_lock`: byte range, owner, pid, nodeid, exclusive/shared mode, and flags.
- `struct lock_waiter`: waiting plock request.
- `struct save_msg`: deferred cluster plock messages saved while a joining node synchronizes state.
- `struct resource_data` and `struct plock_data`: little-endian packed data used for plock state transfer.

Major behavior:
- `setup_plocks()` opens `/dev/misc/dlm_plock` and initializes rate counters.
- `process_plocks()` reads kernel plock requests, identifies the lockspace by fsid, applies rate limiting, and either broadcasts replicated plocks or routes through ownership logic.
- Non-ownership mode replicates each plock to all nodes and frees empty resources eagerly.
- Ownership mode lets a resource have owner `-1` unknown, `0` unowned/replicated, or a nodeid owner. Pending local ops wait until ownership is established.
- `receive_plock()`, `receive_own()`, `receive_sync()`, and `receive_drop()` handle cluster messages, with save-and-replay if `ls->save_plocks` is active.
- Range operations are handled by `lock_internal()` and `unlock_internal()`, using `ranges_overlap()` and `overlap_type()` to split, shrink, convert, or remove locks.
- Waiters are queued on conflicts, canceled through `DLM_PLOCK_OP_CANCEL`, and retried by `do_waiters()` after unlocks/purges.
- `send_all_plocks_data()` serializes local plock state into bounded messages for a joining node; `receive_plocks_data()` reconstructs it.
- `clear_plocks_data()` frees synchronized state.
- `purge_plocks()` removes locks/waiters for a failed node or all locks on unmount, resets owner state when needed, and wakes waiters.
- `copy_plock_state()` formats a human-readable plock dump for query clients.
- `drop_resources_all()` periodically drops unused owned/unowned resources according to `drop_resources_*` options.
- `limit_plocks()` throttles kernel plock reads based on `plock_rate_limit`.

Important dependencies:
- Uses Linux DLM plock ABI from `<linux/dlm_plock.h>`.
- Uses local rb-tree code for fast resource lookup by number.
- Uses local list primitives for resources, locks, waiters, pending ops, and saved messages.
- Uses `linux_endian.h` conversions for cross-node state.
- Uses daemon messaging functions such as `dlm_send_message()` and message types `DLM_MSG_PLOCK*`.
- Uses global daemon options: `enable_plock`, `plock_ownership`, `plock_rate_limit`, and drop-resource tuning.

Notable details:
- GETLK operations from remote nodes are ignored; only local GET replies are written back to the kernel.
- CLOSE unlocks skip result replies and clear waiters for the same owner.
- Ownership transitions are carefully documented with race scenarios around drop, own, and plock messages.
- Locks marked `P_SYNCING` are excluded from checkpoint data because they will be delivered by sync messages.
- `MAX_SEND_SIZE` is 1024 bytes, so large resource state is split into continuation chunks.
