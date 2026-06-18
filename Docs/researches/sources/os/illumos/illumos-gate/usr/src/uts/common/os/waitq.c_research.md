# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/waitq.c

Implements priority-ordered wait queues used for CPU caps and scheduler throttling.

Key responsibilities:
- Initializes and finalizes `waitq_t` structures.
- Maintains a priority-ordered singly linked list of waiting threads with circular doubly linked sublists for equal priorities.
- Enqueues locked threads when a wait queue is unblocked.
- Reorders waiting threads when priority changes.
- Removes one or all waiters and makes them runnable.
- Blocks and unblocks queues as a whole.

Important paths:
- `waitq_link()` inserts a thread by dispatch priority while preserving FIFO order within a priority level.
- `waitq_unlink()` removes a known waiting thread efficiently by using `t_waitq`, priority sublist links, and limited head-list scanning only when needed.
- `waitq_enqueue()` refuses blocked queues, records wait timestamp, marks `TS_DONT_SWAP`, emits DTrace sleep probe state, links the thread, and transitions it to wait state.
- `waitq_change_pri()` unlinks, updates `t_pri`, and relinks the thread in the correct priority position.
- `waitq_setrun()` removes a specific waiter and calls scheduler class `CL_SETRUN()`.
- `waitq_runone()` and `waitq_block()` wake the first or all waiting threads.
- `waitq_unblock()` allows new waiters only after asserting the queue is empty and blocked.

Locking and invariants:
- Each wait queue uses a dispatcher lock.
- Callers must hold the target thread lock for enqueue, priority-change, and explicit setrun paths.
- `waitq_block()` sets `wq_blocked` under lock, then drains all current waiters and asserts the queue is empty.
- `waitq_isempty()` is intentionally lockless and only a hint unless externally synchronized.

Filesystem relevance:
- No direct VFS behavior, but it is kernel scheduling infrastructure. Filesystem and storage threads can be indirectly affected by CPU-cap wait queues and scheduler throttling when they block or are made runnable under system policy.
