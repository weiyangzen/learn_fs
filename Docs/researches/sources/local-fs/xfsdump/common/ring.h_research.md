# File Research: sources/local-fs/xfsdump/common/ring.h

## Role

This header declares the ring buffer/message protocol for asynchronous read-ahead and write-ahead I/O.

## Message Protocol

`ring_msg_t` contains:

- operation
- status
- callback return value
- caller-owned 64-bit user field
- buffer pointer
- private message index and location

Operations include read, write, nop, trace, reset, and die. Status values include init, ok, error, nop ack, ignore, reset ack, and die ack.

## Ring State

`ring_t` exposes performance counters and keeps private queue indexes, semaphores, message array, callback pointers, and client context.

## API

- `ring_create()`
- `ring_get()`
- `ring_put()`
- `ring_reset()`
- `ring_destroy()`

The header comments fully document the required message circulation order, error/ignore behavior, reset semantics, and worker shutdown behavior.
