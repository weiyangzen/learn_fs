# File Research: sources/local-fs/xfsdump/common/ring.c

## Role

This file implements the read-ahead/write-ahead ring abstraction used by drive managers.

A ring is a fixed set of aligned buffers and messages circulating between a client thread and one worker thread.

## Creation

`ring_create()` allocates:

- a ring descriptor
- ready and active semaphores
- message descriptors
- page-aligned buffers via `memalign(PGSZ, bufsz)`

It optionally pins buffers with `mlock()`, maps pinning failures to `E2BIG` or `EPERM`, and starts a worker thread with `cldmgr_create()`.

## Queue Model

Messages move in strict order:

ready queue -> client -> active queue -> worker -> ready queue

`ring_get()` removes the next ready message for the client. `ring_put()` places the client's message on the active queue. Both sides track exactly one held message and assert queue order and message indexes.

## Worker Behavior

`ring_worker_entry()` blocks selected signals, then processes active messages:

- `RING_OP_READ`: invokes client read callback.
- `RING_OP_WRITE`: invokes client write callback.
- `RING_OP_NOP`: acknowledges without I/O.
- `RING_OP_TRACE`: returns ignored status.
- `RING_OP_RESET`: leaves ignore mode and acknowledges reset.
- `RING_OP_DIE`: acknowledges shutdown and exits.

On read/write callback error, the worker enters ignore mode and returns subsequent I/O messages with `RING_STAT_IGNORE` until reset.

## Reset And Destroy

`ring_reset()` sends a reset message, drains ready messages until `RING_STAT_RESETACK`, asserts all messages have returned, reinitializes indexes/statuses, and refills the ready semaphore.

`ring_destroy()` sends a die message, waits for `RING_STAT_DIEACK`, frees semaphores, and frees the ring descriptor.

## Metrics

The ring tracks message attempts, blocking counts, first I/O time, and total I/O count for client and worker performance reporting.
