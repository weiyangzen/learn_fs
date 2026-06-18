# File Research: sources/os/linux/linux/block/blk-mq.c

Purpose: Core Linux block multiqueue implementation. It covers request allocation, bio submission, dispatch, completion, queue freeze/quiesce, CPU hotplug, hctx lifecycle, tag-set allocation, scheduler switching during topology updates, and polling.

Key responsibilities:
- Freezes/unfreezes queues through `q_usage_counter`, `mq_freeze_depth`, and lockdep ownership tracking.
- Quiesces queues/tagsets to stop dispatch while allowing completions.
- Allocates requests from hardware or scheduler tags, including plug-cached batched allocation.
- Converts bios to requests, handles splitting to queue limits, integrity preparation, blk-crypto keyslot handling, rq-qos throttling/tracking, zone write plugging, and flush insertion.
- Attempts plug and scheduler merges before allocating new requests.
- Dispatches directly when budgets and driver tags are available, otherwise inserts into elevator queues, per-CPU software queues, or `hctx->dispatch`.
- Handles dispatch failures from drivers (`BLK_STS_RESOURCE`, `BLK_STS_DEV_RESOURCE`, hard errors) and schedules restarts/delays.
- Tracks request start, timeout, requeue, completion, batched completion, stats, partition accounting, and rq-qos callbacks.
- Routes completions locally, by softirq, or by IPI depending on queue flags and CPU/cache topology.
- Manages per-CPU software queues, hardware context allocation/reuse, flush queues, CPU hotplug callbacks, and software-to-hardware queue mapping.
- Allocates/frees tag sets and request maps, including memory-pressure depth reduction.
- Updates hardware queue counts by temporarily switching elevators to `none`, reallocating hctxs/tags, remapping queues, then restoring elevators.
- Implements sync and async passthrough request execution, cloned request submission for stacking drivers, request cloning helpers, and polled I/O.

Concurrency and lifecycle notes:
- Dispatch uses RCU or SRCU depending on `BLK_MQ_F_BLOCKING`.
- Several memory barriers pair restart/stopped/tag-wait state with dispatch-list insertion to prevent missed queue runs.
- `q_usage_counter` protects queue lifetime during submission, timeout walking, polling, and hctx remapping.
- CPU hotplug marks hctx inactive before draining requests and moves dead-CPU software queue entries to hctx dispatch.
- Request memory is page-backed and freed only after tag SRCU grace periods.
- Queue destruction sets dying state, drains, freezes, syncs work, cancels delayed work, and exits mq resources.

Dependencies:
- Internal block headers: `blk.h`, `blk-mq.h`, `blk-pm.h`, `blk-stat.h`, `blk-mq-sched.h`, `blk-rq-qos.h`.
- Integrates with blk-integrity, blk-crypto, blk-cgroup timing, partition stats, flush state machine, zone write plugging, debugfs/sysfs, CPU hotplug, workqueues, softirqs, and scheduler/elevator ops.

Filesystem/block relevance:
- This is the central path from filesystem bio submission to driver `queue_rq`, and the central completion path back to bios and filesystem I/O waiters.
