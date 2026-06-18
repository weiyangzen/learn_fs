# File Research: sources/os/linux/linux/mm/vmpressure.c

## Role

Memory-cgroup VM pressure accounting and notification implementation. It converts reclaim scan/reclaim efficiency and reclaim priority into low/medium/critical pressure levels, signals registered eventfd listeners, propagates legacy subtree notifications up the memcg hierarchy, and informs in-kernel users such as socket memory pressure handling.

## Key Behavior

- Defines pressure thresholds:
  - A scan window of `SWAP_CLUSTER_MAX * 16` pages rate-limits low-level notifications and smooths medium/critical decisions.
  - Medium pressure begins at 60% reclaim inefficiency.
  - Critical pressure begins at 95% reclaim inefficiency.
  - Reclaim priority at or below `vmpressure_level_critical_prio` is treated as critical pressure.
- Calculates pressure from scanned and reclaimed pages:
  - Reclaimed pages greater than or equal to scanned pages produce low pressure.
  - Otherwise pressure is the percentage of scanning work that failed to reclaim memory.
- Maintains event registrations:
  - `vmpressure_register_event()` parses `low`, `medium`, or `critical`, plus optional `default`, `hierarchy`, or `local` mode, then links an eventfd to the memcg vmpressure object.
  - `vmpressure_unregister_event()` removes the matching eventfd registration.
- Delivers notifications:
  - `vmpressure_event()` filters events by level, ancestor/local mode, and default pass-through semantics before calling `eventfd_signal()`.
  - `vmpressure_work_fn()` drains accumulated tree counters, computes pressure, signals the current memcg, then walks ancestors until the root.
- Accounts reclaim pressure:
  - `vmpressure()` ignores disabled memcg, unsupported legacy non-tree in-kernel accounting, unsuitable GFP contexts, and zero-scanned events.
  - In legacy tree mode it accumulates subtree scanned/reclaimed counters and schedules work once the scan window is reached.
  - In default cgroup/in-kernel mode it tracks local memcg reclaim efficiency and sets socket pressure when pressure exceeds low.
- Accounts reclaim priority:
  - `vmpressure_prio()` injects a critical tree pressure event when reclaim priority is deep enough, using a full scan window with zero reclaimed pages.
- Initializes and cleans up per-memcg structures:
  - `vmpressure_init()` initializes locks, event list, and deferred work.
  - `vmpressure_cleanup()` flushes pending work before the containing memcg object is destroyed.

## Dependencies

Uses memcg and cgroup hierarchy helpers, eventfd, workqueues, spinlocks/mutexes, reclaim GFP masks, swap/vmscan constants, printk debug tracing, and socket pressure integration through memory cgroup helpers.

## Research Notes

`vmpressure.c` is a policy bridge from reclaim behavior to notifications. It intentionally reports only pressure that userspace can plausibly help with, filtering out reclaim constrained to zones such as DMA-only pressure. Legacy userspace notifications use subtree accounting and eventfd propagation, while cgroup v2 in-kernel users use local reclaim efficiency and do not signal root-level pressure.
