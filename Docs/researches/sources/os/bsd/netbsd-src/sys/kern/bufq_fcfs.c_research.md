# File Research: sources/os/bsd/netbsd-src/sys/kern/bufq_fcfs.c

## Purpose
Implements a first-come, first-served buffer queue strategy.

## Main Interfaces
- `BUFQ_DEFINE(fcfs, 10, bufq_fcfs_init)` defines the strategy.
- `bufq_fcfs_put()` appends buffers to the tail with no reordering.
- `bufq_fcfs_get()` returns/removes the head.
- `bufq_fcfs_cancel()` removes a matching queued buffer.
- Init/fini set bufq callbacks and allocate/free private TAILQ state.

## Dependencies
Uses the NetBSD bufq framework, `struct buf`, `TAILQ`, kmem, and module registration.
