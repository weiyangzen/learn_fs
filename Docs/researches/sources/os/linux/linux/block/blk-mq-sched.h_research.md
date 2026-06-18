# File Research: sources/os/linux/linux/block/blk-mq-sched.h

Purpose: Internal header for blk-mq scheduler integration.

Key contents:
- Declares scheduler merge, dispatch, restart, init, exit, and resource allocation APIs.
- Defines `MAX_SCHED_RQ` as the upper scheduler request tag allocation size.
- Provides inline wrappers for scheduler-specific allocation/free callbacks.
- Provides inline scheduler hooks for completion, requeue, allow-merge, and work detection.
- Provides `blk_mq_sched_restart()` restart-bit check and dispatch restart path.
- Provides helpers for setting minimum shallow depth across scheduler tag bitmaps.
- Provides `blk_mq_is_sync_read()` for scheduler policy decisions.

Concurrency and lifecycle notes:
- Inline hooks rely on `RQF_USE_SCHED` to decide whether elevator callbacks are valid.
- `blk_mq_set_min_shallow_depth()` assumes `hctx->sched_tags` is initialized for all hardware queues.

Dependencies:
- Includes `elevator.h` and `blk-mq.h`.

Filesystem/block relevance:
- Defines the narrow internal contract used by blk-mq core and elevator implementations to cooperate on queueing and dispatch.
