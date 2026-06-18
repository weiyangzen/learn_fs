# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/dev/sdev_ncache.c

This file implements the `/dev` negative lookup cache. The cache records names for which implicit reconfiguration failed, preventing repeated expensive `devfsadm` attempts for known-missing devices. It persists through `/etc/devices/devname_cache`.

Major state:
- Tunables for entry expiration, maximum entries, reconfiguration delay, verbose logging, cache disable flags, and read/write disable flags.
- `sdev_boot_state`, `sdev_reconfig_boot`, global `sdev_ncache`, and the nvfile handle for persistent storage.
- `sdev_cache_ops`, which binds nvfile callbacks to `/etc/devices/devname_cache`.

Key routines:
- `sdev_ncache_init()` creates the in-memory list.
- `sdev_ncache_setup()` registers the persistent cache file, reads it unless disabled, processes stored entries, and advances device state.
- `sdev_ncache_unpack_nvlist()` and `sdev_ncache_pack_list()` translate between nvlist storage and internal path/expiration arrays.
- `sdev_ncache_process_store()` loads stored paths into the live negative cache, respecting maximum-entry limits.
- `sdev_ncache_write()` snapshots the live cache to nvfile state and wakes the nvfile flush daemon.
- `sdev_ncache_write_complete()` handles completion and schedules another write if the cache dirtied again during a write.
- `sdev_devstate_change()`, `sdev_state_sysavail()`, and `sdev_state_boot_complete()` manage boot-state transitions, delayed completion, expiration-count decrement, and write enablement.
- `sdev_lookup_filter()` checks whether a failed lookup should avoid reconfiguration.
- `sdev_lookup_failed()` adds eligible failed lookups to the cache.
- `sdev_nc_node_exists()` and `sdev_nc_path_exists()` remove entries when a node/path exists.
- `sdev_nc_free_bootonly()` clears store-sourced entries during reconfiguration boot when reset is enabled.

The cache is protected by both an rwlock for list traversal/mutation and a mutex for dirty/write flags. The backing nvfile has its own lock; the code documents and follows a specific lock ordering during writes.

Risk areas:
- Lock ordering between nvfile lock, negative-cache rwlock, and flag mutex.
- Correctly excluding dynamic, non-global, and `SDEV_NO_NCACHE` nodes.
- Boot-state timing, because cache writes are intentionally delayed until the system is sufficiently available.
