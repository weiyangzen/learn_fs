# File Research: sources/os/linux/linux/mm/page_counter.c

Lockless hierarchical page accounting and limiting support, primarily for memory cgroups and device-memory cgroup counters.

Key responsibilities:
- Provides hierarchical charge, try-charge, uncharge, and local cancel operations for `struct page_counter`.
- Tracks current usage, max limit, failure count, global/local watermarks, and optional protection usage.
- Parses user memory limits into page counts with support for a caller-provided “max” token.
- Computes effective `memory.min` and `memory.low` protection for cgroup reclaim decisions when memcg or cgroup device memory support is enabled.

Important behavior:
- `page_counter_charge()` walks from a counter to its ancestors and atomically adds pages without checking limits.
- `page_counter_try_charge()` speculatively charges each level, checks `max`, rolls back already-charged ancestors on failure, and reports the first counter that exceeded its limit.
- `page_counter_cancel()` subtracts local usage and clamps underflow to zero with a warning.
- Watermarks are intentionally racy statistics; local and global watermarks are updated with `READ_ONCE`/`WRITE_ONCE`.
- Protection propagation stores each child’s protected usage as `min(usage, min)` and `min(usage, low)`, then updates parent aggregate protected usage deltas.
- `page_counter_set_max()` uses an exchange-and-retry sequence so concurrent chargers cannot hide usage above a newly lowered limit.
- `page_counter_set_min()` and `page_counter_set_low()` update settings and refresh protection propagation up the hierarchy.
- Effective protection calculation distributes parent protection according to usage, overcommit, undercommit, and optional recursive protection semantics.

Dependencies:
- Uses `struct page_counter` from `linux/page_counter.h`, atomic long operations, `memparse()`, scheduler rescheduling, and page-size conversion.
- Protection calculation is compiled for `CONFIG_MEMCG` or `CONFIG_CGROUP_DMEM` and is tied to cgroup reclaim semantics.

Notable risks:
- Several statistics are intentionally approximate under races; callers must not treat watermarks or fail counts as strict synchronization.
- `page_counter_try_charge()` speculatively overcharges before rollback, so transient usage can exceed limits.
- Effective protection is stateful and intended for top-down tree iteration; isolated calls can observe stale parent effective values.
- Limit updates require caller-side serialization for the same counter.
