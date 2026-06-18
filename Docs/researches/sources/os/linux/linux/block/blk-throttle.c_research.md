# File Research: sources/os/linux/linux/block/blk-throttle.c

## Scope

This file implements the blk-cgroup I/O throttling policy for bandwidth and IOPS limits. It maintains hierarchical `throtl_grp` service queues, computes per-slice dispatch eligibility, queues over-limit bios, and releases them through timers and the `kthrotld` workqueue.

## Core State

- `struct throtl_data` is per request queue and contains the top-level `throtl_service_queue`, total queued bio counts, and dispatch work.
- `struct throtl_grp` is declared in `blk-throttle.h` and owns cgroup policy data, pending-tree node, service queue, self/parent qnodes, limits, dispatch counters, slices, rule flags, and rwstats.
- `struct throtl_service_queue` has per-direction round-robin qnode lists plus an rb-tree of pending child groups sorted by dispatch time.
- `struct throtl_qnode` separates bios by source and by BPS-vs-IOPS phase so one source cannot fill a parent dispatch list and starve siblings.

## Control Flow

- Policy lifecycle:
  - `throtl_pd_alloc()`, `throtl_pd_init()`, `throtl_pd_online()`, `throtl_pd_offline()`, and `throtl_pd_free()` implement `blkcg_policy_throtl`.
  - `blk_throtl_init()` lazily allocates `q->td`, freezes/quiesces the queue, and activates the blkcg policy.
  - `blk_throtl_exit()` deletes timers, cancels dispatch work, and frees `throtl_data`.
- Bio submission:
  - `__blk_throtl_bio()` starts at `bio->bi_blkg`, checks limits at each hierarchy level, charges pass-through bios, and either climbs to the parent service queue or queues the bio at the first over-limit group.
  - `tg_within_limit()` preserves FIFO behavior: if a group already has queued bios, new bios generally queue behind them, except BPS charging may move a bio into the IOPS phase.
  - Root-blkg priority inversion bios can bypass throttling but still accrue debt through BPS/IOPS charges.
- Dispatch:
  - `throtl_add_bio_tg()` queues bios and activates a group.
  - `tg_update_disptime()` computes the earliest read/write dispatch time using `tg_dispatch_time()`.
  - `throtl_pending_timer_fn()` walks pending children whose dispatch time has arrived, moves bios upward, propagates dispatch through parent groups, or queues top-level `dispatch_work`.
  - `blk_throtl_dispatch_work_fn()` drains ready top-level bios and submits them with plugging.
- Slice accounting:
  - `tg_dispatch_bps_time()` and `tg_dispatch_iops_time()` calculate wait time against BPS/IOPS limits.
  - `throtl_charge_bps_bio()` and `throtl_charge_iops_bio()` advance counters.
  - `throtl_trim_slice()` trims old dispatch debt/credit and prevents old high-rate accounting from creating excessive delays after limit changes.
  - `tg_update_carryover()` preserves already-waited bytes/IOs when limits change while bios remain queued.

## User Interfaces

- Legacy cgroup v1 files include `throttle.read_bps_device`, `throttle.write_bps_device`, `throttle.read_iops_device`, `throttle.write_iops_device`, and service byte/I/O stats including recursive variants.
- Cgroup v2 exposes `io.max` via `throtl_files`, parsing `rbps=`, `wbps=`, `riops=`, and `wiops=` tokens.
- `tg_conf_updated()` recomputes subtree `has_rules` flags, restarts slices, updates pending dispatch times, and reschedules timers.

## Dependencies and Invariants

- Protected primarily by `q->queue_lock`; cgroup traversal uses RCU where appropriate.
- Timers are per service queue and dispatch work runs on `kthrotld_workqueue`.
- `THROTL_TG_PENDING` must match rb-tree membership; `tg_flush_bios()` carefully avoids double insertion while cancelling.
- Default cgroup hierarchy enforces true hierarchical limits; legacy hierarchy keeps the older flat behavior.
