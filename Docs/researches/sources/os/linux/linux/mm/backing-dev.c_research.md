# File Research: sources/os/linux/linux/mm/backing-dev.c

## Purpose
Implements backing-device information lifecycle, sysfs/debugfs exposure, writeback object initialization/shutdown, global BDI registration/lookup, and cgroup writeback object management.

## Main Interfaces
- BDI lifecycle: `bdi_init()`, `bdi_alloc()`, `bdi_register_va()`, `bdi_register()`, `bdi_unregister()`, `bdi_put()`.
- Lookup/metadata: `bdi_get_by_id()`, `inode_to_bdi()`, `bdi_dev_name()`, `bdi_set_owner()`.
- Writeback setup/teardown: `wb_init()`, `wb_shutdown()`, `wb_exit()`.
- Cgroup writeback: `wb_get_lookup()`, `wb_get_create()`, `wb_memcg_offline()`, `wb_blkcg_offline()`.

## Control Flow
Initialization registers the `bdi` class, debugfs root, and global writeback workqueue. BDI registration creates a sysfs device, registers the root writeback, installs debugfs files, marks the writeback registered, assigns a monotonically increasing ID, inserts the BDI into an RB tree and RCU list, and emits a tracepoint. Unregistration removes global visibility, shuts down writeback work, unregisters cgroup writebacks, resets min-ratio accounting, removes debugfs/sysfs objects, and drops owner references.

When cgroup writeback is enabled, per-memcg writeback objects are looked up by memcg CSS ID and validated against the current blkcg association. Missing or stale entries are created with their own refs, lists, work items, memcg/blkcg pins, and BDI references. Offline cleanup kills radix-tree entries, moves writebacks to an offline list, and later switches attached inodes to live ancestors once dirty IO drains.

## State And Synchronization
Uses `bdi_lock` for the global RB tree and BDI list, RCU for list readers, `wb->work_lock` for writeback work registration state, `wb->list_lock` for inode IO lists, and `cgwb_lock` for cgroup writeback trees/lists/offline state. Cgroup writeback release is serialized with `cgwb_release_mutex` and deferred through workqueues plus RCU freeing.

## Integration Points
Connects the writeback subsystem, sysfs class devices, debugfs stats, block cgroup and memory cgroup writeback, inode writeback switching, global dirty throttling, tracepoints, and block-device superblock BDI selection.

## Notable Behaviors
- Exposes BDI tunables for read-ahead, min/max dirty ratios and bytes, strict limit, and a compatibility `stable_pages_required` attribute.
- Debugfs reports per-BDI and per-cgroup writeback dirty/writeback counters and thresholds.
- Root writeback is embedded in each BDI; cgroup writebacks are dynamic and RCU-managed.
- `noop_backing_dev_info` is exported for inodes without a real backing device.

## Risks And Review Focus
- Cgroup writeback teardown is lock/refcount/order sensitive, especially around offline dirty IO.
- Global BDI visibility must be removed before writeback shutdown to avoid new users.
- Sysfs setters must preserve dirty-limit invariants maintained outside this file.
