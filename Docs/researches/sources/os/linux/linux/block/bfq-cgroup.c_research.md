# File Research: sources/os/linux/linux/block/bfq-cgroup.c

`bfq-cgroup.c` provides cgroup integration for the BFQ I/O scheduler. It maps blk-cgroup policy objects to BFQ groups, handles per-cgroup weights and stats, migrates BFQ queues across cgroups, reparents queues on cgroup offline, and supplies no-op/root-only fallbacks when group scheduling is disabled.

Statistics:
- Under `CONFIG_BFQ_CGROUP_DEBUG`, `struct bfq_stat` wraps a percpu counter plus auxiliary atomic count.
- Debug stats include merged I/O, service time, wait time, queued I/O, disk time, average queue size, dequeue count, group wait time, idle time, and empty time.
- Base stats always include bytes and I/O counts through `blkg_rwstat`.
- Dead group stats are transferred to the parent’s auxiliary counters in `bfqg_stats_xfer_dead()` so recursive stats do not lose historical usage.
- Public update helpers include `bfqg_stats_update_io_remove()`, `bfqg_stats_update_io_merged()`, `bfqg_stats_update_completion()`, `bfqg_stats_update_dequeue()`, and debug-only queue/idle/empty timing helpers.

Policy object mapping:
- `bfq_group_data` stores blkcg-level default weight.
- `bfq_group` stores per-device/per-cgroup scheduler state, async queues, rq position tree, stats, active entity counts, and pending-request counts.
- Helpers convert among `blkcg`, `blkcg_gq`, `blkg_policy_data`, `bfq_group_data`, and `bfq_group`.
- `bfq_cpd_alloc/free()` allocate per-blkcg data.
- `bfq_pd_alloc/init/free/reset_stats/offline()` allocate and manage per-device group state.
- `bfq_create_group_hierarchy()` activates `blkcg_policy_bfq` on the disk and returns the root BFQ group.

Queue/group binding:
- `bfq_init_entity()` initializes entity weight, original weight, queue ioprio fields, parent entity, and scheduler data; queue entities pin their BFQ group and blkcg_gq.
- `bfq_bio_bfqg()` selects the online BFQ group associated with a bio’s blkcg, falling back up the hierarchy or to root.
- `bfq_link_bfqg()` fixes internal BFQ parent links for groups that may not yet be connected to the scheduler hierarchy.

Migration:
- `bfq_bic_update_cgroup()` detects task cgroup changes via blkcg serial numbers and moves associated BFQ queues.
- `__bfq_bic_change_cgroup()` handles all actuators and async/sync queues.
- `bfq_sync_bfqq_move()` either moves an unshared sync queue or breaks invalid cooperative merge chains that cross cgroup boundaries.
- `bfq_bfqq_move()` is the main migration routine: it preserves references, updates pending-request accounting, expires/deactivates old scheduling state, drops the old group reference, assigns the new parent/sched_data, reactivates if busy, schedules dispatch when needed, and releases the temporary queue ref.

Cgroup offline:
- `bfq_pd_offline()` runs under scheduler locking, reparents active leaf queues to root, flushes idle trees, deactivates the group entity, releases async queues, and transfers stats.
- `bfq_reparent_active_queues()` and `bfq_reparent_leaf_entity()` walk active trees and in-service entities to find leaf queues.

Weights and files:
- `bfq_group_set_weight()` updates device-specific or default group weight, using a write memory barrier before setting `prio_changed`.
- Legacy files include `bfq.weight`, `bfq.weight_device`, I/O byte/count stats, and many debug stats/recursive stats.
- cgroup v2 exposes `bfq.weight`.
- Allowed weight range is `BFQ_MIN_WEIGHT` to `BFQ_MAX_WEIGHT`.

Fallback without `CONFIG_BFQ_GROUP_IOSCHED`:
- Group movement and blkcg refs become no-ops.
- All bios and queues map to `root_group`.
- A single root `bfq_group` is allocated and service trees initialized.
