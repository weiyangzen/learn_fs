# File Research: sources/os/linux/linux/block/blk-mq.h

Purpose: Internal blk-mq header defining software queue state, allocation metadata, tag APIs, dispatch helpers, queue mapping helpers, and fast inline utilities.

Key contents:
- Defines `blk_mq_ctxs` and `blk_mq_ctx`, the per-CPU software queue state.
- Defines tag constants and internal insertion flags.
- Declares core blk-mq submission, polling, dispatch, sysfs, tag, request-map, and scheduler resource APIs.
- Provides queue mapping helpers for default, read, and poll hardware context types.
- Defines `blk_mq_alloc_data`, used for request/tag allocation.
- Provides tag helpers for reserved tags, shared tags, active request accounting, dispatch budgets, and driver tag acquisition/release.
- Provides `hctx_may_queue()` fairness logic for shared tags.
- Provides dispatch critical-section macro selecting RCU vs SRCU.
- Provides `blk_mq_can_poll()` based on queue limits and poll queue map.

Concurrency and lifecycle notes:
- `blk_mq_hctx_stopped()` includes a memory barrier paired with restart/start paths.
- Active request counters are per-hctx or queue-wide depending on shared-tag mode.
- Shared-tag fairness is enforced before normal driver tag allocation.

Dependencies:
- Public `linux/blk-mq.h`.
- Internal `blk-stat.h`.

Filesystem/block relevance:
- Defines the internal data structures that connect CPU-local bio submission to hardware queue dispatch.
