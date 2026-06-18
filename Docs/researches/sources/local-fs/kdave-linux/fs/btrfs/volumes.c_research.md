# File Research: sources/local-fs/kdave-linux/fs/btrfs/volumes.c

## Purpose

`volumes.c` is the central Btrfs volume, device, chunk, balance, and logical-to-physical mapping implementation. It manages global scanned-device registration, mount-time device opening, seed/sprout filesystems, device add/remove/resize, chunk allocation and removal, balance relocation, RAID profile metadata, runtime chunk maps, block I/O mapping, discard mapping, device statistics, device/chunk-tree verification, and zoned repair relocation.

The file is not just a helper for devices: it is the bridge between on-disk `DEV_ITEM`, `DEV_EXTENT`, `CHUNK_ITEM`, and system-chunk-array state and the in-memory structures used by allocation, relocation, scrub, repair, and every physical block I/O submission path.

## Public Interfaces

Important exported or header-declared interfaces implemented here include:

- RAID/profile helpers: `btrfs_bg_flags_to_raid_index()`, `btrfs_bg_type_to_raid_name()`, `btrfs_nr_parity_stripes()`, `btrfs_describe_block_groups()`, `btrfs_bg_type_to_factor()`, `btrfs_calc_stripe_length()`.
- Global device registry and scanning: `uuid_mutex`, `btrfs_get_fs_uuids()`, `btrfs_cleanup_fs_uuids()`, `btrfs_scan_one_device()`, `btrfs_forget_devices()`.
- Device open/close and superblock reads: `btrfs_open_devices()`, `btrfs_close_devices()`, `btrfs_read_disk_super()`, `btrfs_release_disk_super()`, `btrfs_sb_fsid_ptr()`.
- Device lifecycle: `btrfs_alloc_device()`, `btrfs_init_new_device()`, `btrfs_rm_device()`, `btrfs_grow_device()`, `btrfs_shrink_device()`, `btrfs_update_device()`, `btrfs_scratch_superblocks()`.
- Device lookup helpers: `btrfs_get_dev_args_from_path()`, `btrfs_put_dev_args_from_path()`, `btrfs_find_device_by_devspec()`, `btrfs_find_device()`.
- Device replace helpers: `btrfs_rm_dev_replace_remove_srcdev()`, `btrfs_rm_dev_replace_free_srcdev()`, `btrfs_destroy_dev_replace_tgtdev()`, `btrfs_assign_next_active_device()`.
- Pending/device extent helpers: `btrfs_first_pending_extent()`, `btrfs_find_hole_in_pending_extents()`, `btrfs_remove_dev_extents()`.
- Chunk maps and allocation: `btrfs_find_chunk_map_nolock()`, `btrfs_find_chunk_map()`, `btrfs_get_chunk_map()`, `btrfs_alloc_chunk_map()`, `btrfs_add_chunk_map()`, `btrfs_remove_chunk_map()`, `btrfs_mapping_tree_free()`, `btrfs_create_chunk()`, `btrfs_chunk_alloc_add_chunk_item()`, `btrfs_remove_chunk()`, `btrfs_chunk_writeable()`, `btrfs_update_per_profile_avail()`.
- Balance and relocation: `btrfs_balance()`, `btrfs_resume_balance_async()`, `btrfs_recover_balance()`, `btrfs_pause_balance()`, `btrfs_cancel_balance()`, `btrfs_relocate_chunk()`.
- I/O mapping: `btrfs_num_copies()`, `btrfs_full_stripe_len()`, `alloc_btrfs_io_context()`, `btrfs_get_bioc()`, `btrfs_put_bioc()`, `btrfs_map_discard()`, `btrfs_map_block()`, `btrfs_map_repair_block()`.
- Mount-time loading and validation: `btrfs_read_sys_array()`, `btrfs_read_chunk_tree()`, `btrfs_init_devices_late()`, `btrfs_check_rw_degradable()`, `btrfs_verify_dev_extents()`, `btrfs_verify_dev_items()`.
- Device stats and commit-time updates: `btrfs_init_dev_stats()`, `btrfs_run_dev_stats()`, `btrfs_dev_stat_inc_and_print()`, `btrfs_get_dev_stats()`, `btrfs_commit_device_sizes()`.
- Swapfile/zoned repair helpers: `btrfs_pinned_by_swapfile()`, `btrfs_repair_one_zone()`.

## Major Behavior

The file defines `btrfs_raid_array[]`, the table of Btrfs RAID profile properties: minimum and maximum devices, device increment, copies, parity stripes, tolerated failures, display name, block-group flag, and minimum-device error codes. Many later paths use this table to validate profiles, choose stripe geometry, compute logical capacity, report profile names, select number of copies, and decide degraded/writeability tolerance.

Device registration is built around the global `fs_uuids` list protected by `uuid_mutex`. Scan-time code reads a disk superblock without exclusive open, decides whether single non-seed devices should be skipped, handles temp-fsid cases for single-device duplicate fsids, updates registered paths when devices reappear under a new name, rejects duplicates for already mounted devices, and removes stale unmounted device records. Device names are RCU-protected because list readers and sysfs/ioctl paths can observe them concurrently.

Mount open/close code opens all registered devices, verifies superblock devid/UUID matches, tracks the latest generation device, writeability, discard capability, rotational status, open/rw counts, and per-device block devices. Close paths reset writeable/missing/replace state, flush and invalidate writable block devices, release zone information, clear transient flush-failure state, and keep or free `fs_devices` depending on whether the device set can be reused for later scans.

Seed and sprout handling lets a read-only seed filesystem become part of a new writable filesystem. `btrfs_init_sprout()` clones seed device state, `btrfs_setup_sprout()` splices existing devices into a private seed list and assigns a new fsid to the sprout, and `btrfs_finish_sprout()` records expected seed generations. `btrfs_init_new_device()` handles both normal device add and sprouting, updating superblock totals, sysfs, device items, first writable metadata/system chunks, and post-add relocation of system chunks.

Device extent allocation searches the committed device tree, not only in-memory counters. `find_free_dev_extent()` walks `DEV_EXTENT_KEY` items and adjusts candidate holes for pending chunk allocations recorded in `device->alloc_state`. On zoned filesystems it further requires allocatable, empty, zone-aligned ranges. This prevents double allocation while allowing the caller to know both a suitable hole and the largest available hole if allocation fails.

Device removal first checks extent-tree-v2 support, RAID minimum device constraints, active swapfile pins, replace-target status, and last-writable-device status. It removes writeable devices from allocation, shrinks the device to zero by relocating all extents, deletes the device item, cancels scrub on the device, detaches it from the device lists under `device_list_mutex`, scratches old superblocks, and returns the opened block-device file to the caller for final release outside the sensitive locking context.

Chunk removal is deliberately staged. `btrfs_remove_dev_extents()` deletes corresponding device extents and updates device used-space accounting. `btrfs_remove_chunk()` then holds `chunk_mutex` to update device items, remove the `CHUNK_ITEM`, delete system-chunk-array entries for system chunks, and remove the block group. If system metadata reservation unexpectedly returns `-ENOSPC`, it allocates a new system chunk and retries once before aborting the transaction.

Balance persists its intent as a temporary balance item, validates conversion profiles against the current number of writable devices, rejects mixed data/metadata mismatches, requires force for reducing metadata/system redundancy, and warns when metadata redundancy is lower than data redundancy. The actual balance has a counting pass to populate expected stats and apply limit-min semantics, then a relocation pass that filters chunks by type, profile, usage, devid, physical range, virtual range, stripe count, soft-convert target, and limits. It supports pause, cancel, async resume on remount, mount-time recovery, and special remap-tree metadata chunk processing.

Device shrink temporarily updates in-memory device size and free-space accounting, commits if pending allocations overlap the shrink range, relocates every device extent beyond the new size, retries once after `-ENOSPC`, clears allocation state beyond the new boundary, updates disk total bytes, and rolls back in-memory size/free-space changes on failure. Device grow is simpler: it validates writeability and monotonic size increase, updates superblock/device totals and free chunk space, schedules a commit-time device-size update, and rewrites the device item.

Chunk allocation uses `struct alloc_chunk_ctl` to combine RAID-profile requirements with regular or zoned allocation policy. Regular allocation limits chunks by space-info size, 1 GiB stripe size, and 10% of writable space. Zoned allocation uses zone-sized stripes and stricter metadata/system sizes. The allocator gathers per-device hole information, sorts devices by largest hole and total availability, rounds device count to profile increments, decides stripe/chunk size, installs an in-memory `btrfs_chunk_map`, creates a block group, updates device bytes used, sets RAID incompat bits, and later persists the chunk item/device extent state through `btrfs_chunk_alloc_add_chunk_item()`.

The in-memory mapping tree is an rb-tree of `btrfs_chunk_map` objects protected by `mapping_tree_lock`. Maps are refcounted, inserted with device allocation-state bits set, removed with bits cleared, and used by both mount-time chunk loading and runtime I/O. Lookup can return intersecting maps as well as exact containing maps for callers that scan through all chunks.

I/O mapping translates logical ranges into physical stripes for every Btrfs profile. It limits mapped length at stripe or full-stripe boundaries, chooses live mirrors for RAID1/RAID10 according to read policy while avoiding a device-replace source when possible, handles DUP and SINGLE mapping, maps RAID0/RAID10 striping, maps RAID56 reads to the rotated data stripe, maps RAID56 writes/recovery to all full-stripe data/parity stripes, and optionally uses the RAID stripe tree for remapped reads. Single-device mappings can be returned through a stack `btrfs_io_stripe`; multi-stripe mappings allocate `btrfs_io_context`.

Device replace is integrated into write mapping. While replace is active, writes to source-device stripes are duplicated to the target device unless the block group is already flagged for zoned copy. RAID56 replacement records the source stripe index, and DUP read-mirror enumeration collapses duplicate replacement target stripes so callers see a stable mirror set.

Discard mapping maps logical discard ranges to per-device discard stripes, including RAID0/RAID10 stripe spreading and mirrored/DUP fanout. RAID56 discard is explicitly unsupported. The function can translate remapped logical ranges before building discard stripes.

Mount-time loading reads the superblock system chunk array first, then walks the chunk tree to load all device items and chunk items. Device-item loading opens seed devices when fsids differ, creates missing device placeholders for degraded mounts, validates seed generations, fills device geometry/accounting from disk, and populates free chunk space. Chunk-item loading creates runtime maps, validates 32-bit metadata limits on 32-bit systems, resolves missing devices, marks devices as present in filesystem metadata, and adds maps to the mapping tree.

Validation after mount checks whether rw degraded mounting is safe for every chunk, verifies every device extent has a matching chunk stripe with the expected length and device boundary/zone alignment, verifies every chunk stripe has a corresponding device extent, and reports registered devices that were not found in the chunk tree. These checks protect later allocation/free paths from corrupt or stale device/chunk metadata.

Device statistics are loaded from and persisted to the device tree. The commit path first does a cheap RCU scan for dirty counters to avoid blocking transaction commit on long `device_list_mutex` holders such as FITRIM, then writes changed stats items with explicit memory-barrier pairing against atomic stat updates. Ioctl-facing stats can read or reset counters.

Zoned repair support starts a background relocation task for a block group after an I/O failure. It avoids repair attempts on non-zoned filesystems and degraded mounts, marks the block group as already relocating for repair, obtains balance exclusivity, optionally preallocates a data chunk, and relocates the affected chunk.

## Dependencies and Integration

`volumes.c` depends on most core Btrfs subsystems: disk I/O and superblock handling, extent tree and block-group creation/removal, transactions, RAID56, device replace, sysfs, tree checker/accessors, space info, discard, zoned support, UUID tree, ioctl balance formatting, relocation, scrub, superblock helpers, and the RAID stripe tree. It also interfaces directly with Linux block-device open/close, page cache, VFS path lookup, kthreads, RCU, rbtrees, list sorting, atomics, percpu counters, and lockdep.

The file is a major integration point for `ioctl.c` device/balance/resize commands, transaction commit, scrub and repair, chunk allocator callers, mount and remount flows, degraded mount policy, device replace finalization, FITRIM/discard, and read/write bio submission.

## Concurrency and Safety Notes

The top-of-file locking comment is operationally important. `uuid_mutex` protects the global scanned filesystem list and mount/open/close transitions. `device_list_mutex` protects per-filesystem device list mutations and coordinates with RCU readers. `chunk_mutex` protects chunk allocation/removal, device used-space accounting, post-commit device update lists, and system chunk array changes. `balance_mutex` protects balance control state. `reclaim_bgs_lock` serializes relocation/removal against automatic unused block-group cleanup.

Lock ordering is intentionally constrained: `uuid_mutex` may nest `device_list_mutex`, `chunk_mutex`, and `balance_mutex`; device replace finalization uses `device_list_mutex` before `chunk_mutex`; several paths avoid taking one lock because COW or block-device open paths could recurse into allocation or kernel open locks. Comments around chunk removal, chunk item insertion, mount-time chunk-tree loading, and device removal document these deadlock-avoidance choices.

RCU is used for device list traversal and device names. Paths that detach devices call `synchronize_rcu()` before freeing. The mapping tree uses explicit refcounting, and callers must drop chunk maps with `btrfs_free_chunk_map()`.

High-risk areas are RAID geometry arithmetic, device-replace duplication, RAID56 full-stripe boundaries, zoned alignment and empty-zone checks, seed/sprout fsid transitions, degraded mount missing-device policy, balance pause/cancel lifetime, transaction abort handling during chunk/device metadata updates, and commit-time stat/device-size synchronization.
