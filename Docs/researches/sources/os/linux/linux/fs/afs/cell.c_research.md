# File Research: sources/os/linux/linux/fs/afs/cell.c

Purpose: manages AFS cell records: lookup, allocation, DNS/VL server refresh, root cell setup, proc activation, lifecycle references, timers, garbage collection, and purge.

Key interfaces:
- `afs_find_cell()`, `afs_lookup_cell()`, `afs_cell_init()`.
- `afs_get_cell()`, `afs_put_cell()`, `afs_use_cell()`, `afs_unuse_cell()`.
- `afs_queue_cell()`, `afs_set_cell_timer()`, `afs_cell_purge()`.

Implementation notes:
- Cells live in a per-net RB tree keyed case-insensitively by lowercase cell name.
- Allocation validates names, stores name and key description in one allocation, creates an initial VL server list from configured addresses or DNS-unavailable placeholder, assigns dynamic-root inode numbers, and initializes locks/timers/work.
- Lookup may preallocate a candidate outside `cells_lock`, then insert or discard it if another thread won.
- Cell state is published with release ordering and waiters use `wait_var_event`.
- DNS updates query AFSDB/SRV/text records, classify lookup status, clamp TTL between min and max, and RCU-replace the VL server list when useful.
- Active counts are separate from object refs. Dropping the final active use schedules a management timer; final object free is workqueue plus RCU.
- Manager transitions setup to unlooked/active, performs DNS lookup when requested, expires inactive cells, deactivates proc entries, purges servers, removes from RB tree, releases root volume, and marks dead.
- Purge unpins root/workstation cells, queues all cells, and waits for `cells_outstanding` to reach zero.

Dependencies:
- DNS resolver, VL server list management, proc cell setup/removal, server purge, volume refs, workqueues, timers, RB tree, RCU.

Edge cases:
- Configured VL server addresses bypass DNS expiry by setting `TIME64_MAX`.
- Root cell validation rejects empty, leading/trailing dot, slash, and double-dot names.
- On lookup failure after activation, active references are dropped with `afs_unuse_cell()`.
