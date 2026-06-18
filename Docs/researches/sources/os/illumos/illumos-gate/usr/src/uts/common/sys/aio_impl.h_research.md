# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/aio_impl.h

## Purpose

`aio_impl.h` defines kernel-private asynchronous I/O request, list-I/O notification, and per-process AIO state.

## Main Structures

`aio_lio_t` is a list-I/O group head with request count, active reference count, free-list pointer, completion condition variable, signal queue pointer, and event-port notification data.

`aio_req_t` wraps the driver-visible `struct aio_req` with fd, flags, result pointer, cancel callback, queue/hash links, LIO group, embedded `uio`, `iovec`, `buf`, signal notification, user aiocb pointer union, and event-port data.

`aio_t` is per-process AIO state: pending/outstanding counts, flags, cleanup state, port queues, free lists, done/poll/notify/cleanup queues, mutexes/CVs, aiocb pointer table, waitn state, notification counts, port queue lock, and request hash table.

## Interfaces

The header declares `aphysio`, page-unlock, cleanup, zero-length completion, request free, queue concatenation, result copyout, port queue removal, enqueue/dequeue, and `aio_done()` for driver/PXFS use.

## Research Notes

This is the kernel AIO engine’s internal contract. The risky areas are queue membership flags, process-exit cleanup, port/signal notification ordering, and physical I/O buffer lifetime.
