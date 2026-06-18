<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/include/flow/TaskQueue.h -->
# sources/storage-engines/foundationdb/flow/include/flow/TaskQueue.h

Purpose: This header defines the Flow run-loop task queue for ready tasks, delayed timers, and cross-thread task injection. It is main-thread-owned except for `addReadyThreadSafe`.

Important APIs and types: `template <typename Task> class TaskQueue` exposes `addReady`, `addTimer`, `addReadyThreadSafe`, `canSleep`, `getSleepTime`, `processReadyTimers`, `processThreadReady`, ready-task accessors, `popReadyTask`, `initMetrics`, and `clear`. Internal types are `OrderedTask`, `DelayedTask`, and a reservable `ReadyQueue`.

Control flow: Ready tasks enter a priority queue with a computed FIFO priority `(taskPriority << 32) - issueCounter`, so higher task priority wins and same-priority tasks remain FIFO. Timers enter a min-time priority queue with reversed comparison. Cross-thread producers push into `ThreadSafeQueue`; the main thread drains it in `processThreadReady`. `canSleep` checks both local ready queue and the thread-safe queue's sleep marker.

State and persistence behavior: State is in-memory queues plus `tasksIssued` and metric handles. There is no persistence. Under ASAN, `clear` deletes pending tasks to satisfy leak sanitizer and intentionally triggers broken promises; in normal builds it swaps queues away without deleting task objects.

Dependencies and integration points: It depends on `TDMetric`, `network`, `ThreadSafeQueue`, `TaskPriority`, and DTrace probes from `Platform.h`. It is a central piece of `INetwork` run-loop scheduling and side-thread wakeup integration.

Risks: All non-thread-safe methods must remain on the network/main thread. `tasksIssued` overflow would affect FIFO ordering, though the 64-bit range is large. ASAN-only cleanup behavior differs from production shutdown behavior. `ThreadSafeQueue::pop` can transiently appear empty during a producer window, which the ASAN drain loop accounts for.

Test signals: Tests should cover priority ordering, FIFO among equal priorities, timer readiness with `TIME_EPS`, cross-thread wake return value, `canSleep` wake protocol, metric increments, and ASAN cleanup behavior where applicable.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/include/flow/TaskQueue.h -->
