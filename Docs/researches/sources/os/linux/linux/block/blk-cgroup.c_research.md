# File Research: sources/os/linux/linux/block/blk-cgroup.c

## Scope

This file implements the common block I/O controller cgroup core: blkcg/blkg allocation and teardown, cgroup callbacks, policy registration and disk activation, per-bio blkcg association, rstat-backed I/O accounting, optional async bio punting, and delay-based throttling.

## Core APIs and Entry Points

- Blkg/disk lifecycle:
  - `blkg_init_queue()`, `blkcg_init_disk()`, `blkcg_exit_disk()`.
  - Internal `blkg_alloc()`, `blkg_create()`, `blkg_lookup_create()`, `blkg_destroy()`, `blkg_destroy_all()`.
- Policy lifecycle:
  - `blkcg_policy_register()`, `blkcg_policy_unregister()`.
  - `blkcg_activate_policy()`, `blkcg_deactivate_policy()`.
- Configuration helpers:
  - `blkg_conf_init()`, `blkg_conf_open_bdev()`, `blkg_conf_open_bdev_frozen()`, `blkg_conf_prep()`, `blkg_conf_exit()`, `blkg_conf_exit_frozen()`.
- Stats:
  - `blk_cgroup_bio_start()`, `blkcg_print_blkgs()`, `__blkg_prfill_u64()`, `blkcg_print_stat()`.
- Bio association:
  - `bio_blkcg_css()`, `bio_associate_blkg_from_css()`, `bio_associate_blkg()`, `bio_clone_blkg_association()`.
- Delay/throttle:
  - `blkcg_add_delay()`, `blkcg_schedule_throttle()`, `blkcg_maybe_throttle_current()`, `blk_cgroup_congested()`.

## Major State

- Global:
  - `blkcg_root`, `blkcg_root_css`, `blkcg_policy[]`, `all_blkcgs`.
  - `blkcg_pol_register_mutex` serializes whole policy register/unregister operations.
  - `blkcg_pol_mutex` protects policy arrays and activation/deactivation.
  - `blkg_stat_lock` serializes stat propagation.
- Per blkcg:
  - `blkg_tree`, `blkg_hint`, `blkg_list`, per-policy `cpd[]`, `online_pin`, `congestion_count`, per-cpu `lhead` stat lists.
- Per blkg:
  - `q`, `blkcg`, `parent`, `refcnt`, online flag, per-cpu `iostat_cpu`, aggregate `iostat`, policy `pd[]`, delay accounting, RCU/free work.

## Control Flow

- `blkcg_init_disk()` waits for any old root blkg cleanup on shared queues, allocates the root blkg, creates it under queue lock, and stores `q->root_blkg`.
- Blkg creation walks from root down so every non-root blkg has a valid parent. Creation may return the closest existing blkg if allocation fails during lookup.
- Blkg destruction offlines per-policy data, removes cgroup tree/list links, clears hints, and kills the percpu ref. Actual freeing is RCU-delayed and then workqueue-delayed because policy free and queue release can sleep.
- Cgroup destruction is staged around writeback: offline writeback first, wait for `online_pin` release, destroy blkgs, then free the blkcg.
- `blk_cgroup_bio_start()` updates per-cpu bytes/ios, queues the per-cpu stat node on the blkcg lockless list, and notifies cgroup rstat.
- `__blkcg_rstat_flush()` drains only queued stat nodes, updates global blkg stats, and propagates deltas up the parent blkg chain.
- Policy activation freezes mq queues, allocates missing per-blkg policy data parent-first, handles GFP_NOWAIT failure by preallocating with GFP_KERNEL outside the queue lock, and rolls back on allocation failure.
- Delay throttling accumulates nanosecond delay per blkg; tasks are marked for notify-resume and sleep in user-return context rather than while holding I/O locks.

## Dependencies

- Cgroup core: css allocation/online/offline/free, cftypes, rstat, writeback integration.
- Block core: request queues, disks, queue freeze, `queue_lock`, `blkdev_get_no_open()`.
- Policy users include io priority and throttle code via `blk-ioprio.h` and `blk-throttle.h`.
- Kernel infra: radix tree, hlist/list, percpu refs, RCU, lockless llist, u64 stats, workqueues, PSI.

## Risks and Invariants

- Lock ordering is strict: queue lock nests outside blkcg lock in most paths; `blkcg_destroy_blkgs()` uses trylock/reschedule loops to avoid reverse-lock deadlocks.
- Blkg pointers are RCU protected, but only local stats/rate-limit fields are safe without a ref; queue and policy data require correct locks or refs.
- `blkg_conf_prep()` returns with queue lock held and must be paired with `blkg_conf_exit()`.
- Root cgroup stats are synthesized from disk stats rather than normally flushed blkg iostats.
- Bio association failure during cgroup teardown intentionally walks up to the closest live parent blkg.
- Delay code caps normal accumulated delay to 250 ms per syscall unless explicit non-decaying delay mode is used.
