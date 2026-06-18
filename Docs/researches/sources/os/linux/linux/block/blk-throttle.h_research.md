# File Research: sources/os/linux/linux/block/blk-throttle.h

## Scope

This header defines the internal data structures and inline gating logic for blk-cgroup throttling. It is shared by the implementation and block submission paths that decide whether a bio should enter `__blk_throtl_bio()`.

## Core Structures

- `struct throtl_qnode` wraps source-specific BPS and IOPS bio lists and the owning `throtl_grp`.
- `struct throtl_service_queue` contains parent linkage, read/write qnode queues, queued BPS/IOPS counts, pending child rb-tree, first pending dispatch time, and pending timer.
- `enum tg_state_flags` tracks rb-tree membership, empty-to-nonempty transitions, IOPS empty transitions, and cancellation state.
- `struct throtl_grp` embeds `blkg_policy_data` first, then cgroup throttling state: rb-node, owning `throtl_data`, service queue, self/parent qnodes, dispatch time, rule flags, BPS/IOPS limits, dispatch counters, slice timing, and rwstats.

## Core APIs

- `blkcg_policy_throtl` is exported for blkcg policy registration and lookups.
- `pd_to_tg()` and `blkg_to_tg()` convert policy data or blkcg queue objects to throttle groups.
- Without `CONFIG_BLK_DEV_THROTTLING`, `blk_throtl_exit()`, `blk_throtl_bio()`, and `blk_throtl_cancel_bios()` compile to no-ops.
- With throttling enabled:
  - `blk_throtl_activated()` checks that `q->td` exists and the policy is active.
  - `blk_should_throtl()` checks cgroup accounting/statistics and rule flags.
  - `blk_throtl_bio()` is the fast inline gate before calling `__blk_throtl_bio()`.

## Dependencies and Invariants

- Relies on blk-cgroup policy data, `bio_data_dir()`, bio flags (`BIO_CGROUP_ACCT`, `BIO_BPS_THROTTLED`), and `blkg_rwstat`.
- IOPS limits are always counted; BPS limits skip bios already marked `BIO_BPS_THROTTLED`.
- On non-default cgroup hierarchy, this inline path updates legacy throttling stats for bytes and I/Os.
