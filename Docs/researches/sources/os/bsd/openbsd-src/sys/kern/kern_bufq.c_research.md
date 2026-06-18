# File Research: sources/os/bsd/openbsd-src/sys/kern/kern_bufq.c

Kernel buffer queue implementation for block I/O scheduling.

Key behavior:
- Provides pluggable queue implementations through `struct bufq_impl`.
- Supports FIFO and n-scan queue types.
- `bufq_init()` initializes per-queue mutex, high/low outstanding thresholds, implementation storage, and global queue registration.
- Thresholds are reduced when buffer-cache KVA slots are limited, preventing writes from consuming all buffer KVA.
- `bufq_queue()`, `bufq_dequeue()`, and `bufq_peek()` wrap implementation operations with locking.
- `bufq_wait()` throttles when outstanding buffers reach high water.
- `bufq_done()` decrements outstanding count and wakes waiters below low water.
- `bufq_drain()` completes all pending buffers with `ENXIO`.
- `bufq_quiesce()` stops queue mutation and waits for outstanding buffers to drain.
- `bufq_restart()` resumes all queues and wakes blocked initializers/queuers.
- FIFO uses `SIMPLEQ`.
- N-scan keeps a sorted segment plus FIFO backlog, sorting up to `BUFQ_NSCAN_N` requests by block number.

Filesystem/OS relevance:
- Directly tied to block-device buffer scheduling and filesystem writeback behavior.
- Quiesce/restart behavior is relevant to suspend, detach, and storage reset paths.
