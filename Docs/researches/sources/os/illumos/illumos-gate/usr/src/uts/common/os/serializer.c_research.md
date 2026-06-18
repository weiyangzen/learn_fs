# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/serializer.c

## Purpose

Implements kernel serializers: a general-purpose mechanism that executes submitted callbacks one at a time in arrival order, commonly as a lighter alternative to STREAMS outer perimeters.

## Data Model

- `serializer_t` contains a mutex, condition variable, owner thread, taskq-pending flag, queued message list, queue count, and debug-only current callback/message/argument fields.
- Queued work is represented by reusing `mblk_t` fields: `b_queue` stores the callback and `b_prev` stores the argument.

## Key Interfaces

- `serializer_init()` creates the kmem cache.
- `serializer_create()` allocates a serializer.
- `serializer_enter()` executes immediately if unowned, otherwise queues the request and returns. The owner drains queued work up to `serializer_credit`, then may schedule taskq drain work.
- `serializer_wait()` waits until no owner, no pending taskq drain, and no queued messages remain.
- `serializer_destroy()` waits and then frees the serializer.
- Internal `serializer_exec()`, `serializer_enqueue()`, `serializer_drain()`, and `serializer_drain_completely()` perform callback execution and queue draining.

## Concurrency Behavior

- The first entering thread becomes owner and executes work directly.
- Threads entering while owned append to the FIFO queue and return.
- To prevent a producer from draining indefinitely, direct draining is limited by `serializer_credit`; remaining work may be continued by `system_taskq`.
- `serializer_wait()` must not be called from within the serializer and asserts against owner recursion.

## Dependencies

Uses kernel mutexes, condition variables, taskq dispatch, kmem caches, STREAMS message blocks, and DTrace SDT probes for enqueue and execution boundaries.

## Notes for Future Work

- Callers must pass an `mblk_t` with `b_next` and `b_prev` clear; the serializer temporarily owns these fields.
- If taskq dispatch fails, direct draining can continue in later `serializer_enter()` calls.
