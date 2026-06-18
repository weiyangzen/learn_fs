# File Research: sources/os/linux/linux/block/blk-settings.c

Purpose: Validates, initializes, commits, and stacks block queue limits and related queue properties.

Key responsibilities:
- Sets request timeout through `blk_queue_rq_timeout()`.
- Initializes stacking-device limits with conservative inherit/maximum values.
- Applies queue limits to backing device readahead and I/O page settings.
- Validates zoned-device limits, integrity metadata/protection information, atomic write constraints, discard, segment, DMA, and block-size constraints.
- Calculates effective `max_sectors`, discard limits, write-zeroes limits, zone append limits, and atomic-write limits.
- Commits queue limit updates under `q->limits_lock`, optionally freezing the queue.
- Stacks bottom-device limits into top-device limits for MD/DM-like stacking drivers.
- Stacks integrity profiles only when compatible.
- Updates queue depth and notifies rq-qos modules.
- Computes partition-aware alignment and discard alignment.

Concurrency and lifecycle notes:
- Limit commits require `q->limits_lock`; frozen variant freezes blk-mq around the update.
- Inline encryption and integrity are rejected together when unsupported.
- Stacking code tracks misalignment through `BLK_FLAG_MISALIGNED` and returns warning status while still producing safe limits.

Dependencies:
- Core block headers, blk-integrity, T10 PI, CRC64 PI, rq-qos, writeback throttling.
- Math helpers for gcd/lcm and power-of-two constraints.

Filesystem/block relevance:
- Queue limits determine bio splitting, alignment validity, discard behavior, integrity handling, zoned write sizing, and maximum I/O sizes visible to filesystems and stacking drivers.
