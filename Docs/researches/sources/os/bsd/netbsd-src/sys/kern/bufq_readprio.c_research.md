# File Research: sources/os/bsd/netbsd-src/sys/kern/bufq_readprio.c

## Purpose
Implements a read-priority buffer queue strategy with FCFS reads and sorted writes.

## Main Interfaces
- `BUFQ_DEFINE(readprio, 30, bufq_readprio_init)` registers the strategy.
- `bufq_prio_put()` appends reads to the read queue and inserts writes into a sorted write queue.
- `bufq_prio_get()` selects reads first, then serves a burst of writes after `PRIO_READ_BURST` reads when writes are pending.
- `bufq_prio_cancel()` removes a buffer from read or write queues and resets current selection.

## Implementation Notes
Reads are prioritized up to 48 consecutive requests; then 16 write requests may be served. `bq_write_next` tracks the rotating write position.

## Dependencies
Uses bufq infrastructure, `TAILQ`, buffer flags such as `B_READ`, `buf_inorder()`, kmem, and module registration.
