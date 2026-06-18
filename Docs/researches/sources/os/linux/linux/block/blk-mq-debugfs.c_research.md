# File Research: sources/os/linux/linux/block/blk-mq-debugfs.c

## Summary
Implements debugfs support for blk-mq queues, hardware contexts, software contexts, schedulers, rq-qos policies, tags, flags, and request lists.

## Main Responsibilities
- Create queue-level debugfs files such as `state`, `pm_only`, `requeue_list`, and `zone_wplugs`.
- Expose hardware-context state, flags, dispatch lists, busy requests, tag bitmaps, active count, and type.
- Expose per-CPU context request lists.
- Register scheduler and rq-qos debugfs subdirectories and attributes.
- Format request operations, command flags, rq flags, tags, and state.

## Key APIs
- `__blk_mq_debugfs_rq_show()`.
- `blk_mq_debugfs_rq_show()`.
- `blk_mq_debugfs_register()`.
- `blk_mq_debugfs_register_hctx()`.
- `blk_mq_debugfs_unregister_hctx()`.
- `blk_mq_debugfs_register_hctxs()`.
- `blk_mq_debugfs_unregister_hctxs()`.
- `blk_mq_debugfs_register_sched()`.
- `blk_mq_debugfs_unregister_sched()`.
- `blk_mq_debugfs_register_sched_hctx()`.
- `blk_mq_debugfs_unregister_sched_hctx()`.
- `blk_mq_debugfs_register_rq_qos()`.

## Important Behavior
The queue `state` file accepts `run`, `start`, and `kick`, which invoke `blk_mq_run_hw_queues()`, `blk_mq_start_stopped_hw_queues()`, and `blk_mq_kick_requeue_list()`. It refuses writes once the queue is dying.

Request-list seq files lock the relevant list while iterating: `q->requeue_lock`, `hctx->lock`, or `ctx->lock`. Busy request reporting uses `blk_mq_tagset_busy_iter()` under `q->elevator_lock`.

`debugfs_create_files()` asserts `q->debugfs_mutex` and also asserts that `elevator_lock` and `rq_qos_mutex` are not held, avoiding lock nesting under locks that may be acquired while a queue is frozen.

## State and Synchronization
Debugfs dentries are stored on queues and hardware contexts. Registration and scheduler/rq-qos directory creation are serialized by `q->debugfs_mutex`; individual readers use the locks appropriate to the data they expose.

## Risks
Debugfs output observes live request state, so request state may change during reads. The writeable `state` operation is diagnostic but can actively kick queues, so it must remain unavailable after queue teardown begins.
