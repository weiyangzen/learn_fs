<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/include/flow/ThreadSafeQueue.h -->
# sources/storage-engines/foundationdb/flow/include/flow/ThreadSafeQueue.h

Purpose: This header implements a multi-producer, single-consumer queue with a low-overhead sleep/wake protocol for Flow's event loop.

Important APIs and types: `template <class T> class ThreadSafeQueue` exposes `push`, `canSleep`, and `pop`. Internal nodes are an atomic `BaseNode`, heap-allocated `Node`, plus `stub` and `sleeping` sentinel nodes.

Control flow: Producers allocate a node and atomically exchange it into the head, linking it from the previous head. The single consumer advances `tail` through linked nodes in `popNode`. `canSleep` inserts the `sleeping` sentinel when the queue appears empty; a later `push` returns true if it linked after that sentinel, signaling the caller should wake the consumer.

State and persistence behavior: State is an in-memory MPSC linked queue. The destructor drains any remaining nodes. There is no persistence.

Dependencies and integration points: It depends on atomics, Flow `Optional`, `FastAllocated`, and Valgrind annotations. `TaskQueue` uses it for cross-thread ready tasks; other side-thread producers can use it for main-thread handoff.

Risks: The algorithm is "almost" lock-free; if a producer stalls in the narrow window between `head.exchange` and linking `prev->next`, the consumer can temporarily return empty. Only one consumer may call `canSleep` and `pop`. Misusing the sleep protocol can lose wakeups or cause unnecessary wakeups.

Test signals: Tests should cover many producers with one consumer, FIFO-like delivery expected by the algorithm, transient empty tolerance, `canSleep` returning true only when wake is needed, destructor draining, and stress under TSAN/Valgrind.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/include/flow/ThreadSafeQueue.h -->
