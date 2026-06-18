# File Research: sources/os/linux/linux/block/blk-mq-tag.c

Purpose: Implements blk-mq driver/scheduler tag allocation, freeing, wakeups, active-queue fairness, request iteration, and tag-map allocation.

Key responsibilities:
- Uses `sbitmap_queue` for normal and reserved tag pools.
- Tracks active queues for shared-tag fairness and recalculates wake batches.
- Allocates single tags, batched tags, and reserved tags.
- Sleeps on tag wait queues unless allocation is `BLK_MQ_REQ_NOWAIT`.
- Revalidates CPU-to-hctx mapping after sleeping because CPU hotplug may remap the allocation target.
- Frees tags singly or in batches.
- Iterates busy requests safely for queue/tagset timeout, inflight, and teardown logic.
- Allocates and frees `blk_mq_tags`, including delayed freeing of request pages through SRCU callbacks.
- Resizes shared hardware and scheduler tag bitmaps.
- Builds queue-wide unique tags from hctx index plus per-hctx tag.

Concurrency and lifecycle notes:
- Request iteration increments request refs unless iterating static request arrays.
- `tags_srcu` protects tag maps and delayed freeing of request memory.
- `__blk_mq_tag_busy()` / `__blk_mq_tag_idle()` maintain shared-user accounting under `tags->lock`.
- Allocation handles inactive hctx by releasing the tag and returning `BLK_MQ_NO_TAG`.

Dependencies:
- Internal blk-mq helpers and scheduler tag helpers.
- Kernel `sbitmap_queue`, RCU/SRCU, kmemleak, and page allocation.

Filesystem/block relevance:
- Tags are the scarce per-device queue slots that gate request submission from filesystem bios to drivers.
