# File Research: sources/os/linux/linux-stable/fs/afs/cell.c

This file manages AFS cell records, root/workstation cell setup, DNS updates for VL servers, lifecycle references, proc exposure, timers, and garbage collection.

Major responsibilities:
- Looks up cells by name in a network namespace rb-tree.
- Allocates cells with normalized lowercase names, key descriptions, VL server lists, locks, timers, volume/server trees, and dynamic root inode numbers.
- Creates or finds cells through `afs_lookup_cell()`, including preallocation outside locks and duplicate insertion handling.
- Sets or replaces the root/workstation cell from module/proc configuration.
- Refreshes VL server lists from DNS with TTL clamping and DNS status translation.
- Activates cells in procfs, deactivates them, purges servers, and removes dead cells from rb-trees.
- Maintains both reference count and active-use count.

Cell states:
- Cells progress through setting up, unlooked, active, removing, and dead states.
- State changes use release stores and wakeups so waiters observe preceding error/status updates.
- Lookup callers may wait for active/dead unless they are preloading/root/dynroot paths.
- Dead cells return their stored error to lookup callers.

DNS behavior:
- `afs_update_cell()` calls `afs_dns_query()`, maps DNS/resolver errors to `DNS_LOOKUP_*` statuses, clamps expiry between min and max TTL, and replaces the VL server list when useful.
- Configured address lists are treated as `DNS_RECORD_FROM_CONFIG` and can satisfy active lookup without DNS success.
- DNS lookup count is release-published for waiters.

Lifecycle:
- `afs_use_cell()` increments both reference and active counters.
- `afs_unuse_cell()` decrements active, sets an inactivity timestamp, may arm a GC timer, then drops the reference.
- Inactive cells with VL servers are retained for `afs_cell_gc_delay`; live namespace shutdown expires them immediately.
- Final destruction cancels timers/work, RCU-frees the cell, drops VL server lists, alias/root references, anonymous key, dynamic inode ID, and name storage.
- `afs_cell_purge()` unpins root cell and no-GC cells, queues management, and waits for all cells outstanding.
