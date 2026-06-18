# File Research: sources/os/linux/linux/block/blk-cgroup-rwstat.c

## Scope

This file implements legacy block-cgroup read/write stat helpers enabled by `CONFIG_BLK_CGROUP_RWSTAT`. The header explicitly marks them as legacy and not for new code.

## Core APIs

- `blkg_rwstat_init()` initializes `BLKG_RWSTAT_NR` percpu counters and zeroes auxiliary counters.
- `blkg_rwstat_exit()` destroys the percpu counters.
- `__blkg_prfill_rwstat()` prints a sampled rwstat for one device.
- `blkg_prfill_rwstat()` reads a rwstat at an offset inside policy data and prints it.
- `blkg_rwstat_recursive_sum()` walks a blkg subtree and sums local plus auxiliary counts.

## Control Flow

- Printing emits per-device `Read`, `Write`, `Sync`, `Async`, `Discard`, and `Total` lines.
- Recursive summing walks descendants with `blkg_for_each_descendant_pre()` under RCU while the caller holds the queue lock for stable online checks.
- If `pol` is non-NULL, `off` is relative to the blkg policy data; otherwise it is relative to `struct blkcg_gq`.

## Dependencies

- `blk-cgroup-rwstat.h` types and inline add/read/reset helpers.
- `blk-cgroup.h` traversal and policy-data helpers.
- `percpu_counter_*`, `atomic64_t`, `seq_file`.

## Risks and Invariants

- The caller of recursive summing must hold `blkg->q->queue_lock`.
- Auxiliary counters carry stats of dead children and are included in recursive totals but excluded from local `blkg_rwstat_read()`.
- Since these are legacy helpers, new policies should prefer the newer iostat/rstat path in `blk-cgroup.c`.
