# File Research: sources/os/linux/linux/mm/mmzone.c

Small zone, pgdat, zonelist, LRU-vector, and NUMA balancing helpers.

Key responsibilities:
- Provides online-node iteration helpers `first_online_pgdat()` and `next_online_pgdat()`.
- Provides `next_zone()` for `for_each_zone()` style zone iteration across node boundaries.
- Provides `__next_zones_zonelist()` for allocation zonelist scanning subject to highest zone index and optional NUMA nodemask.
- Initializes `struct lruvec` state, including lock, zswap state, LRU list heads, unevictable-list poisoning, and multi-gen LRU state.
- Provides `folio_xchg_last_cpupid()` when NUMA balancing stores last CPU/PID outside page flags abstraction.

Important behavior:
- `__next_zones_zonelist()` skips zones above the caller’s allowed highest zone and, on NUMA, zones whose node is not in the nodemask.
- `lruvec_init()` deliberately deletes/poisons the unevictable LRU list head because unevictable pages are not actually threaded on that list.
- `folio_xchg_last_cpupid()` updates encoded folio flag bits with a compare-exchange loop and returns the old cpupid.

Dependencies:
- Online node APIs, `NODE_DATA`, zonelists, LRU definitions, zswap lruvec state, multi-gen LRU initialization, NUMA balancing flags, and folio flag atomic updates.

Notable risks:
- Zonelist scanning must preserve sentinel behavior and not dereference invalid zone references.
- Unevictable LRU list poisoning is intentional; code must not treat it like a normal list.
- The cpupid exchange path depends on correct flag bit masks and atomic retry semantics.
