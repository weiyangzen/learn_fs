<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/9p_req_queue.h -->
# sources/user-network-fs/nfs-ganesha/src/include/9p_req_queue.h

## Purpose
`9p_req_queue.h` declares the 9P request queue infrastructure used to classify and dispatch incoming 9P requests through producer and consumer queues with cache-line padding and wait-list wakeups.

## Important APIs, types, and functions
- `struct req_q` is a spinlock-protected glist queue with `size`, `max`, and waiter count.
- `struct req_q_pair` separates a decoder-side `producer` queue from an executor-side `consumer` queue, padded with `GSH_CACHE_PAD`.
- `enum req_q_e` currently defines `REQ_Q_LOW_LATENCY` and `N_REQ_QUEUES`.
- `struct req_q_set` groups all queue pairs.
- `struct _9p_req_st` contains global request counters, queue set, aggregate size, a state spinlock, wait list, and waiter count.
- `_9p_rpc_q_init()` initializes a queue list and spinlock; `_9p_rpc_q_destroy()` tears down the spinlock.
- `_9p_queue_awaken()` walks wait-list entries and signals both left and right wait queue condition variables.

## Control flow
Queue users initialize `struct req_q` objects before accepting requests. Producers and consumers coordinate with spinlocks around glist operations in implementation code outside this header. When work becomes available or state changes, `_9p_queue_awaken()` locks the request-state spinlock, iterates waiters, and signals both condition variables in each `wait_q_entry_t`.

## State and persistence
All queue state is in memory and tied to the 9P service runtime. Queue sizes, max counts, counters, and waiters are transient scheduling state; no persistence is involved.

## Dependencies and integration points
The header depends on `gsh_list.h`, `common_utils.h`, `gsh_wait_queue.h`, pthread spinlocks, Ganesha wait-queue entries, and cache-padding macros. It integrates the 9P decoder/executor pipeline with Ganesha's wait queue primitives.

## Risks
- The comment says LIFO for `struct req_q::q`; scheduling behavior depends on implementation code preserving expected order.
- Wakeups signal condition variables while holding the request-state spinlock; waiters must follow compatible locking rules to avoid missed wakeups or lock-order deadlocks.
- Only one queue class is currently declared. Adding classes requires updating queue initialization and dispatch logic outside this header.
- Queue `max` is not initialized by `_9p_rpc_q_init()`, so callers must set or tolerate its default separately.

## Test signals
- Threaded queue tests should cover producer/consumer handoff, waiter wakeups, queue destroy after drain, and repeated awaken with empty wait list.
- Static analysis should verify all queue pairs are initialized and destroyed.
- Performance tests should check cache-line padding keeps hot producer/consumer state from false sharing.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/9p_req_queue.h -->
