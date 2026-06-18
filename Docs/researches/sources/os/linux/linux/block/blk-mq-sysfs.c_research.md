# File Research: sources/os/linux/linux/block/blk-mq-sysfs.c

Purpose: Owns sysfs exposure and kobject lifetime for blk-mq queue topology under each disk’s `mq/` directory.

Key responsibilities:
- Creates `mq/`, hardware context kobjects, and per-CPU context child kobjects.
- Exposes hardware context attributes: `nr_tags`, `nr_reserved_tags`, and `cpu_list`.
- Initializes and releases `blk_mq_ctxs`, per-CPU `blk_mq_ctx` kobjects, and `blk_mq_hw_ctx` kobjects.
- Registers and unregisters all hardware contexts when a disk queue is registered/unregistered.
- Supports unregister/register of only hctx nodes during hardware queue remapping.

Concurrency and lifecycle notes:
- `blk_mq_hw_sysfs_show()` takes `q->elevator_lock` while reading hctx scheduler-sensitive state.
- Full registration is protected by `q->tag_set->tag_list_lock`.
- Release functions free per-CPU contexts, hctx cpumasks, ctx maps, and hctx arrays at kobject final release.

Dependencies:
- Internal blk-mq structures from `blk-mq.h`.
- Generic kernel kobject/sysfs infrastructure.

Filesystem/block relevance:
- Provides observability of blk-mq topology and tag capacities used by block devices backing filesystems.
