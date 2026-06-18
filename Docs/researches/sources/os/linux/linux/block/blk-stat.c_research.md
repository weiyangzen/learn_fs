# File Research: sources/os/linux/linux/block/blk-stat.c

Purpose: Implements per-queue request latency/stat callbacks used by block throttling and monitoring features.

Key responsibilities:
- Defines `blk_queue_stats`, holding callback list, lock, and accounting reference count.
- Initializes, sums, and updates `blk_rq_stat` min/max/mean/sample data.
- Records request latency samples in per-CPU per-bucket stats on completion.
- Aggregates per-CPU stats on timer expiration and invokes callback timer function.
- Allocates, registers, removes, and RCU-frees stat callbacks.
- Enables/disables accounting and maintains `QUEUE_FLAG_STATS`.
- Allocates and frees queue stats containers.

Concurrency and lifecycle notes:
- Completion sampling walks callbacks under RCU and uses `get_cpu()` for per-CPU stat access.
- Callback registration/removal uses `q->stats->lock` plus RCU list operations.
- Callback freeing is deferred with `call_rcu()`.
- Timer is synchronously deleted during callback removal.

Dependencies:
- `blk-stat.h`, `blk-mq.h`, and core block queue flags.

Filesystem/block relevance:
- Supplies latency samples consumed by block-layer policy mechanisms that influence filesystem I/O scheduling and throttling.
