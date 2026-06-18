# File Research: sources/os/bsd/netbsd-src/sys/kern/bufq_priocscan.c

## Purpose
Implements a priority-aware cyclical scan buffer queue strategy using red-black trees.

## Main Interfaces
- `BUFQ_DEFINE(priocscan, 40, bufq_priocscan_init)` registers the strategy.
- `cscan_put()` and `cscan_get()` maintain per-priority CSCAN ordered queues.
- `bufq_priocscan_selectqueue()` maps `BIO_GETPRIO()` classes to three priority queues.
- `bufq_priocscan_get()` chooses which priority queue to serve, enforcing burst limits when multiple queues are non-empty.
- `bufq_priocscan_cancel()` searches all priority queues and removes a matching buffer.

## Implementation Notes
Each priority queue has a CSCAN last-position key unless global-position mode is enabled. Burst defaults are 64, 16, and 4 requests for high, medium, and low priority, trading throughput and latency.

## Dependencies
Uses bufq, `struct buf`, `BIO_GETPRIO()`, `rb_tree`, kmem, and module registration.
