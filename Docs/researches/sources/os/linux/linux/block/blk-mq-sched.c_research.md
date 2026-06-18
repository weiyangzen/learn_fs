# File Research: sources/os/linux/linux/block/blk-mq-sched.c

Purpose: Implements the blk-mq I/O scheduler bridge: dispatching requests from elevator queues or per-CPU software queues into hardware queues, scheduler tag allocation, scheduler initialization/teardown, and scheduler debugfs registration.

Key responsibilities:
- Tracks scheduler restart state with `BLK_MQ_S_SCHED_RESTART`, using memory barriers to avoid missed dispatch after requests are added to `hctx->dispatch`.
- Dispatches scheduler-owned requests through `blk_mq_do_dispatch_sched()` and non-elevator software-queue requests through `blk_mq_do_dispatch_ctx()`.
- Handles residual dispatch-list requests before pulling new requests from the scheduler to preserve merge/sort opportunities.
- Supports schedulers that can dispatch requests mapped to multiple hardware contexts by sorting and batching by `rq->mq_hctx`.
- Implements default software-queue bio merge fallback when no elevator `bio_merge` op exists.
- Allocates and frees scheduler request tags through `elevator_tags`, including shared-tag mode.
- Coordinates batch scheduler resource allocation during hardware queue count changes.
- Initializes and exits scheduler instances through elevator ops `init_sched`, `init_hctx`, `exit_hctx`, and `exit_sched`.

Concurrency and lifecycle notes:
- Uses `list_empty_careful()`, `hctx->lock`, scheduler restart bits, and explicit `smp_mb()` pairing with core dispatch.
- Batch scheduler resource code assumes `set->update_nr_hwq_lock` write ownership and documents safe unlocked elevator access under that lock.
- Scheduler tag teardown clears `hctx->sched_tags` and `q->sched_shared_tags` before resources are freed.

Dependencies:
- Internal blk-mq core helpers from `blk-mq.h`.
- Elevator interfaces from `elevator.h`.
- Debugfs hooks from `blk-mq-debugfs.h`.
- Writeback throttling header `blk-wbt.h`.

Filesystem/block relevance:
- This is the policy insertion point between filesystem bios and hardware dispatch when an I/O scheduler is configured.
