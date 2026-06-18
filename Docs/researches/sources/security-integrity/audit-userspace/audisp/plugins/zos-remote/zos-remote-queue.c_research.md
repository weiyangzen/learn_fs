# sources/security-integrity/audit-userspace/audisp/plugins/zos-remote/zos-remote-queue.c

Purpose: Provides the z/OS remote plugin's private producer/consumer queue for `BerElement *` requests. It decouples auparse callback encoding on the main thread from synchronous LDAP submission on the submit thread.

Important APIs, types, and functions: Exports `init_queue()`, `enqueue()`, `dequeue()`, `nudge_queue()`, `increase_queue_depth()`, and `destroy_queue()`. Internal state is a circular array `q`, guarded by `queue_lock` and signaled with `queue_nonempty`; indices are `q_next` and `q_last`, and capacity is `q_depth`.

Control flow: `init_queue()` allocates and NULL-initializes the ring and initializes mutex/condition variables. `enqueue()` tries the next slot up to four attempts, yielding between attempts if the slot is occupied; on success it stores the BER pointer, advances `q_next`, signals the condition, and unlocks. `dequeue()` waits while the next consumer slot is NULL, removes the pointer, clears the slot, advances `q_last`, and returns it. `nudge_queue()` signals the condition without adding data, allowing signal handlers to wake the consumer. `increase_queue_depth()` reallocates only when the requested size is larger and fills new slots with NULL. `destroy_queue()` frees all remaining BER objects with `ber_free(..., 1)`, frees the ring, and destroys synchronization primitives.

State and persistence: State is entirely in memory. Queue contents persist only until submitted, dropped, or process exit. The queue owns any BER remaining in a slot at destruction time, but on full-queue drop `enqueue()` logs and returns without freeing the caller's BER.

Dependencies and integration points: Depends on pthreads, liblber's `BerElement` and `ber_free()`, scheduler yield support, and local logging. It is used by `zos-remote-plugin.c` as the handoff between `push_event()` and `submission_thread_main()`.

Risks and edge cases: `nudge_queue()` can wake `dequeue()`, but `dequeue()` loops until a slot is non-NULL and has no direct stop flag, so a wake with no data will not return NULL unless another mechanism changes the queue state. This can make shutdown/reload depend on pending events or cancellation. `increase_queue_depth()` uses `realloc()` on the ring without preserving FIFO order for wrapped live data and without coordinating with a concurrent enqueue/dequeue beyond the mutex around resize; if only one resizer exists this is likely acceptable, but the wrapped-copy behavior is weaker than the newer generic audisp queue. Full queue drops do not free the BER, creating a leak in the current caller contract.

Test signals: No direct unit tests in this subset. The generic `audisp/queue.c` has much stronger test coverage for resizing and overflow, but this queue has different condition-variable semantics and should be separately tested for shutdown nudges, full queue leaks, and resize-after-wrap behavior.
