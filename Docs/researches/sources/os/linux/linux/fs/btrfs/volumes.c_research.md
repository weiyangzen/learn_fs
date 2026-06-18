# File Research: sources/os/linux/linux/fs/btrfs/volumes.c

## Scope

This file is in subset A through `sources/os/linux/linux`. I read the full file, all 8,868 lines.

## Purpose

`fs/btrfs/volumes.c` is the core Btrfs volume, device, chunk, balance, and logical-to-physical mapping implementation. It owns the in-memory and on-disk relationship between:

- scanned block devices and `struct btrfs_fs_devices`
- mounted `struct btrfs_device` instances
- device items and device extents in Btrfs trees
- chunk items and the in-memory chunk mapping rb-tree
- RAID/profile geometry for allocation and I/O mapping
- balance, relocation, resize, add/remove, seed/sprout, degraded mount, and device stats

## Main Data And Tables

- `btrfs_raid_array[]` is the central RAID/profile attribute table. It defines per-profile device minimums, maximums, device increments, copies, parity, tolerated failures, stripe geometry, flags, names, and minimum-device error codes for RAID10, RAID1, RAID1C3, RAID1C4, DUP, RAID0, SINGLE, RAID5, and RAID6.
- `struct btrfs_io_geometry` is a local mapping scratch structure used by `btrfs_map_block()` to calculate stripe index, stripe number, mirror, RAID56 full-stripe boundaries, max errors, operation type, and stripe-tree use.
- `struct alloc_chunk_ctl` is the chunk allocation control bundle. It carries selected RAID attributes, allocation limits, stripe size, chunk size, device count, and target `space_info`.
- `struct remap_chunk_info` tracks metadata-remap block groups selected by balance for special remap-tree handling.
- `fs_uuids` plus `uuid_mutex` is the global registry of scanned filesystem device sets.

## Locking Model

The file documents and follows a layered locking model:

- `uuid_mutex` protects the global `fs_uuids` registry, mount-time device assembly, stale device cleanup, seeding/sprout transitions, and open/close lifetime transitions.
- `fs_devices->device_list_mutex` protects updates to each filesystem device list and coordinates with sysfs, scrub, replace finishing, and superblock writing.
- `fs_info->chunk_mutex` protects chunk allocation/removal, chunk tree changes, system chunk array changes, device allocation state, per-profile availability, and transaction post-commit device update lists.
- `balance_mutex`, `balance_lock`, and exclusive operation state serialize balance with device add/remove/replace/resize.
- `reclaim_bgs_lock` serializes relocation/removal paths with automatic unused block-group reclamation.
- RCU is used for read-mostly device list and device-name access where appropriate.

The explicit lock nesting comment is important: `uuid_mutex` may nest `device_list_mutex`, which may nest `chunk_mutex`; `uuid_mutex` may also nest `balance_mutex`.

## Device Registration And Scanning

The scan path reads superblocks from block devices, identifies fsids and device ids, and records devices in global `fs_uuids`.

Key functions:

- `btrfs_get_bdev_and_sb()` opens a block device, optionally sets Btrfs block size, invalidates cached state, and reads a disk superblock.
- `btrfs_read_disk_super()` reads a superblock mirror through the block-device mapping, validates magic/bytenr, and NUL-terminates labels defensively.
- `btrfs_scan_one_device()` does non-exclusive scan-time open, reads the primary superblock, skips registration for single-device non-seed scans where safe, calls `device_list_add()`, and frees stale aliases.
- `device_list_add()` is the central registry mutation path. It handles new fsids, `METADATA_UUID`, temp-fsid single-device handling, duplicate devices, missing-device reappearance, path replacement, generation ordering, and stale-device avoidance.
- `find_fsid_by_device()` handles the special temp-fsid case for single-device filesystems with duplicate fsids on different devices.
- `btrfs_skip_registration()` avoids cluttering the global list for ordinary single-device scans but keeps mounted path aliases discoverable.

Important behavior:

- Single-device non-seed filesystems can be skipped during non-mount scans.
- Devices with the same fsid but different block device can receive a temporary fsid when eligible.
- A mounted missing device may be updated if it reappears with a valid path.
- Duplicate devices with different `devt` are rejected to avoid accidentally replacing the wrong device.
- Stale unmounted devices are removed by `btrfs_free_stale_devices()` and exposed through `btrfs_forget_devices()`.

## Device Lifetime

The file allocates, opens, closes, clones, and frees device sets.

Key functions:

- `alloc_fs_devices()` initializes an unlinked `btrfs_fs_devices`.
- `btrfs_alloc_device()` creates a `btrfs_device`, generates or sets devid/UUID, initializes allocation state, ordered-data state, lists, stats, and optional path.
- `btrfs_free_device()` releases path, allocation state, zoned info, and the device object.
- `free_fs_devices()` frees all devices from a closed/unheld `fs_devices`.
- `btrfs_open_one_device()` validates devid and UUID against the disk superblock, records bdev/file, sets writeability, detects seeding, updates devt, and adds writable devices to the allocation list.
- `btrfs_open_devices()` sorts devices by devid and opens the set under `uuid_mutex`.
- `btrfs_close_one_device()` removes allocation-list membership, clears missing/writeable/replace/flush state, closes bdev, releases zone info and allocation state, and resets per-mount fields.
- `btrfs_close_devices()` closes primary and seed device sets and frees single-device unheld assemblies when possible.
- `btrfs_free_extra_devids()` removes scanned devices that are not present in filesystem metadata after the chunk tree is read.

## Missing, Degraded, Seed, And Sprout Handling

The file handles seed devices and read-write sprouting:

- `btrfs_init_sprout()` creates a private seed-device copy and preserves the original scanned seed fs in `fs_uuids`.
- `btrfs_setup_sprout()` moves old devices to a seed list, generates a new fsid for the sprouted filesystem, clears seeding flags, and resets writable-device counters.
- `btrfs_finish_sprout()` updates seed device generations in device items.
- `open_seed_devices()` opens or constructs seed fs device sets while mounting a filesystem that references seed fsids.
- `read_one_dev()` moves missing seed devices into the correct private seed device set if needed.
- `handle_missing_device()` and `add_missing_dev()` construct missing placeholders only when degraded mount is allowed.

The code enforces that seed devices remain read-only and that generation checks match when a device belongs to a seed fs_devices rather than the sprout.

## Device Add, Remove, Grow, And Shrink

Main entry points:

- `btrfs_init_new_device()` implements device add. It opens the target for write, validates zone compatibility and size, rejects duplicates, allocates a new device, starts a transaction, updates device/sysfs/super counters, handles seed sprouting, creates initial writable chunks if needed, inserts the device item, commits, relocates system chunks after sprout, forgets stale aliases, and updates device timestamps for userspace probing.
- `btrfs_rm_device()` implements device remove. It rejects unsupported extent tree v2, checks RAID minimum device counts, rejects pinned swapfile devices and replace targets, removes the device from allocation, shrinks it to zero by relocating its extents, removes the device item, detaches it from lists, updates super device count, scratches superblocks, and returns the bdev file to the caller for final release.
- `btrfs_grow_device()` increases a writable non-replace device size, updates super total bytes, total writable bytes, free chunk space, per-profile availability, transaction post-commit update list, and the device item.
- `btrfs_shrink_device()` reduces a device size. It first updates in-memory size and free-space accounting, commits pending chunk allocations if needed, relocates all device extents beyond the new size, then commits the new disk size and super total bytes. On error it restores the original in-memory size and free-space counters.

Important constraints:

- Device remove and relocation are unavailable for extent tree v2 in this file.
- Active swapfile pins block device removal and block-group relocation.
- Replace target devices are excluded from normal allocation and resize flows.
- Shrink uses `reclaim_bgs_lock` around chunk lookup/relocation to avoid races with unused block-group deletion.

## Device Extent Allocation And Freeing

Device extents represent physical allocation on devices.

Key functions:

- `btrfs_first_pending_extent()` and `btrfs_find_hole_in_pending_extents()` account for in-memory pending chunk allocations stored in `device->alloc_state`.
- `find_free_dev_extent()` searches the committed device tree for holes, then filters those holes against pending allocations and zoned constraints.
- `dev_extent_hole_check_zoned()` uses zoned-device helpers to find allocatable zones and ensure empty zones.
- `btrfs_free_dev_extent()` deletes a device extent item and marks the transaction as having freed block groups.
- `btrfs_remove_dev_extents()` deletes all device extents for a chunk map, updates per-device `bytes_used`, free chunk space, and post-commit device update lists.

The allocation search deliberately uses the commit root and pending allocation state so new chunk allocation does not double-allocate physical space in the current transaction.

## Chunk Mapping Tree

The in-memory chunk mapping tree maps logical byte ranges to device stripes.

Key functions:

- `btrfs_find_chunk_map_nolock()`, `btrfs_find_chunk_map()`, and `btrfs_get_chunk_map()` search the rb-tree and return referenced `btrfs_chunk_map` objects.
- `btrfs_add_chunk_map()` inserts a map, marks physical device ranges as `CHUNK_ALLOCATED`, and clears `CHUNK_TRIMMED`.
- `btrfs_remove_chunk_map()` erases a map and clears device allocation bits.
- `btrfs_mapping_tree_free()` releases all maps at teardown.
- `btrfs_alloc_chunk_map()` allocates variable-sized chunk maps for a stripe count.

The search function supports overlapping-range lookup, including callers that pass `U64_MAX` length to find the next map at or after a logical offset.

## Chunk Allocation

Chunk allocation chooses devices, stripe sizes, chunk sizes, creates an in-memory map, creates a block group, then later persists chunk/device extent items.

Key functions:

- `btrfs_create_chunk()` is the main allocator under `chunk_mutex`.
- `init_alloc_chunk_ctl()` loads profile geometry from `btrfs_raid_array[]` and dispatches to regular or zoned policy setup.
- `init_alloc_chunk_ctl_policy_regular()` sets normal max chunk/stripe limits and reserves the first device range.
- `init_alloc_chunk_ctl_policy_zoned()` fixes stripe size to zone size and sizes chunks by block-group type.
- `gather_device_info()` collects writable, metadata-present, non-replace devices with free holes.
- `decide_stripe_size_regular()` maximizes device participation, bounds chunk size, caps stripe size, and aligns to `BTRFS_STRIPE_LEN`.
- `decide_stripe_size_zoned()` keeps stripe size fixed at zone size and reduces device count if needed.
- `create_chunk()` builds the map, inserts it into the mapping tree, creates the block group, updates device bytes used, free chunk space, RAID incompat flags, and per-profile availability.
- `btrfs_chunk_alloc_add_chunk_item()` persists the chunk item, updates device items, and adds system chunks to the superblock system array when needed.
- `init_first_rw_device()` creates initial metadata and system chunks during seed sprout before normal writable metadata can be allocated.

Important invariants:

- Chunk tree updates, system chunk array updates, and device item updates for chunk allocation are protected by `chunk_mutex`.
- System chunks are limited to `BTRFS_MAX_DEVS_SYS_CHUNK`.
- RAID56 and RAID1C3/RAID1C4 allocations set their corresponding incompat feature flags.
- Allocation excludes missing, read-only, non-metadata, and replace-target devices.

## Chunk Removal And Relocation

Chunk removal splits into deleting device extents, deleting chunk items/system array entries, and removing the block group.

Key functions:

- `btrfs_remove_chunk()` obtains the map, removes device extents, reserves system metadata, deletes the chunk item, optionally allocates a new system chunk and retries on `-ENOSPC`, deletes the superblock system chunk entry if applicable, updates per-profile availability, releases reserved chunk metadata, and removes the block group.
- `remove_chunk_item()` updates each device item and deletes the chunk item.
- `btrfs_del_sys_chunk()` removes a system chunk from the superblock system chunk array.
- `btrfs_relocate_chunk()` relocates all extents in a block group, pauses scrub during relocation, and then either finishes chunk removal or leaves remap-tree relocation to separate handling.
- `btrfs_relocate_sys_chunks()` scans all system chunks backward and relocates them, with one retry for ENOSPC.
- `btrfs_may_alloc_data_chunk()` preallocates a data chunk when relocating the only data chunk so profile availability is preserved.

## Balance

The file contains the balance engine, persistent state, filters, pause/cancel/resume, and metadata-remap handling.

Persistent state:

- `insert_balance_item()` writes `BTRFS_BALANCE_OBJECTID` temporary item.
- `del_balance_item()` deletes it.
- `btrfs_recover_balance()` loads it at mount and marks the exclusive operation as paused balance.
- `reset_balance_state()` clears in-memory state and deletes the on-disk item.

Filters:

- profile, usage, usage range, devid, device physical range, logical range, stripe count, soft convert, and limit filters are implemented by `chunk_*_filter()` helpers and composed in `should_balance_chunk()`.

Execution:

- `btrfs_balance()` validates mixed-group constraints, allowed target profiles by writable device count, metadata/system redundancy reduction, and metadata-vs-data redundancy. It persists state, sets running state, drops `balance_mutex`, runs `__btrfs_balance()`, then handles paused/canceled/completed cleanup.
- `__btrfs_balance()` does a counting pass and an execution pass over chunk items from high to low offsets, applies filters, optionally reserves a data chunk, relocates selected chunks, records ENOSPC, and processes metadata-remap chunks through `balance_remap_chunks()`.
- `balance_remap_chunks()` marks remap block groups read-only, COWs the remap tree, marks unused block groups, drops RO state, and releases refs.
- `btrfs_resume_balance_async()` starts a `btrfs-balance` kthread after read-write remount if a balance was paused.
- `btrfs_pause_balance()` and `btrfs_cancel_balance()` coordinate with running balance via atomic request counters and wait queues.

## Logical To Physical I/O Mapping

`btrfs_map_block()` is the main I/O mapping entry point. It maps logical ranges to one stack `btrfs_io_stripe` or an allocated `btrfs_io_context`.

Mapping behavior:

- Fetches the chunk map and translates remapped logical ranges through the remap tree when needed.
- Computes maximum I/O length so operations do not cross stripe or RAID56 full-stripe boundaries.
- Selects mirror and stripe geometry according to profile:
  - RAID0: stripe by modulo over `num_stripes`.
  - RAID1/RAID1C3/RAID1C4: reads choose one live mirror; writes return all mirrors.
  - DUP: reads choose a mirror; writes return both copies.
  - RAID10: maps through sub-stripe groups and chooses live mirror for reads.
  - RAID5/RAID6: reads map a data stripe directly; writes and recovery map full stripe sets with parity rotation.
  - SINGLE: maps by stripe modulo and reports mirror number as stripe index plus one.
- Avoids source device during device replace reads when configured.
- Duplicates non-read writes to the replace target through `handle_ops_on_dev_replace()`.
- Uses `set_io_stripe()` to optionally consult the RAID stripe tree for read offsets.
- Uses stack `smap` fast path for single-device mappings.

Related helpers:

- `find_live_mirror()` implements read policy, missing-device avoidance, and device-replace source avoidance.
- Experimental read policies include PID, round-robin, and preferred devid when `CONFIG_BTRFS_EXPERIMENTAL` is enabled.
- `btrfs_num_copies()` returns mirror/retry count for a logical range.
- `btrfs_full_stripe_len()` returns RAID56 full-stripe length.
- `btrfs_map_discard()` maps discard ranges to physical stripes and rejects RAID56 discard.
- `btrfs_map_repair_block()` maps read-repair/scrub repair writes to exactly one device, including special RAID56 repair stripe selection.

## Device Replace Integration

The file participates in replace finishing and write duplication:

- `btrfs_rm_dev_replace_remove_srcdev()` removes the source device from lists and counters.
- `btrfs_rm_dev_replace_free_srcdev()` closes and frees the old source device and removes empty seed fs_devices if needed.
- `btrfs_destroy_dev_replace_tgtdev()` removes sysfs, list membership, counters, scratches superblocks, closes, and frees a failed target device.
- `handle_ops_on_dev_replace()` duplicates writes from source stripes to the target device unless the block group is zoned and marked `TO_COPY`.
- `btrfs_map_block()` holds `dev_replace.rwsem` across mapping when a replace is ongoing so commit-time replacement cannot mutate devices under an I/O mapping.

## Mount-Time Chunk And Device Loading

The file reconstructs in-memory state from superblock and trees:

- `btrfs_read_sys_array()` reads system chunks from the superblock system array using a dummy extent buffer.
- `btrfs_read_chunk_tree()` scans device items first, then chunk items, with chunk-tree locking skipped because the filesystem is not open yet. It validates total device counts and total bytes.
- `read_one_dev()` loads one device item, opens seed devices if fsid differs, creates missing placeholders when degraded, moves missing devices into seed sets if appropriate, validates size against the bdev, sets item-found and in-metadata state, and updates free chunk space for writable devices.
- `read_one_chunk()` creates a chunk map from an on-disk chunk item, finds or creates missing device objects for its stripes, sets in-metadata bits, calculates stripe size, and inserts the map.
- `btrfs_init_devices_late()` attaches `fs_info` to devices after mount setup and loads zoned information for seed devices.

## Degraded And Writeability Checks

- `btrfs_check_rw_degradable()` walks all chunk maps and verifies each chunk has no more missing or flush-failed devices than its profile tolerates.
- `btrfs_chunk_writeable()` checks whether a specific chunk has writable devices and enough non-missing stripes.
- `btrfs_check_raid_min_devices()` validates that the current device count can support all currently available profiles.
- `btrfs_num_devices()` subtracts an ongoing replace target from the count for min-device checks.

## Device Stats

The file persists and reports per-device error stats:

- `btrfs_init_dev_stats()` initializes stats for all primary and seed devices.
- `btrfs_device_init_dev_stats()` reads a device stats item or initializes zero stats.
- `btrfs_run_dev_stats()` runs during transaction commit, first using an RCU quick check to avoid taking `device_list_mutex` when no stats changed, then updates changed items.
- `update_dev_stat_item()` inserts, replaces too-small, or updates the persistent stats item.
- `btrfs_dev_stat_inc_and_print()` increments an error counter and rate-limited prints current write/read/flush/corruption/generation errors.
- `btrfs_get_dev_stats()` serves ioctl stats reads and optional reset.

The memory-barrier comments in `btrfs_run_dev_stats()` document ordering between `dev_stats_ccnt` and in-memory counter reads.

## Verification And Repair

Mount/write safety verification:

- `btrfs_verify_dev_extents()` scans the device tree to ensure device extents are ordered, non-overlapping, mapped to chunk stripes, within device boundaries, and zone-aligned on zoned devices.
- `verify_one_dev_extent()` checks one dev extent against its chunk map and increments `map->verified_stripes`.
- `verify_chunk_dev_extent_mapping()` ensures every chunk stripe had a matching dev extent.
- `btrfs_verify_dev_items()` checks that every registered primary and seed device has a corresponding device item, except the replace target devid.
- `btrfs_pinned_by_swapfile()` checks whether a block group or device is pinned by an active swapfile.
- `btrfs_repair_one_zone()` starts asynchronous relocation repair for a zoned block group after I/O failure unless the filesystem is degraded.
- `relocating_repair_kthread()` performs exclusive-operation relocation repair for the affected block group.

## Superblock And Userspace Side Effects

- `btrfs_scratch_superblocks()` clears all superblock mirrors on a removed/rejected device, using zone reset for zoned devices.
- `update_dev_time()` updates device path timestamps to help userspace probing tools such as blkid.
- Device add/remove paths emit sysfs updates and uevents where appropriate.
- `btrfs_commit_device_sizes()` updates committed in-memory device sizes during transaction commit from `dev_update_list`.

## Error Handling Patterns

Common error handling patterns include:

- Return negative errno for kernel/internal errors and Btrfs-specific positive error constants for ioctl-visible device/profile constraints.
- Abort transactions for critical on-disk update failures after partial chunk/device metadata mutation.
- Use `-EUCLEAN` for detected logical corruption such as impossible chunk item matches, missing dev extents, invalid chunk/device mappings, or inconsistent device items.
- Retry selected ENOSPC paths once, especially system chunk relocation and chunk removal requiring system metadata.
- Preserve in-memory counters on failure by undoing allocation-list, total-byte, free-space, and sysfs changes in device add/remove/resize error paths.

## External Interfaces Provided By This File

Prominent non-static entry points include:

- Device registry/lifetime: `btrfs_scan_one_device`, `btrfs_open_devices`, `btrfs_close_devices`, `btrfs_forget_devices`, `btrfs_cleanup_fs_uuids`, `btrfs_get_fs_uuids`
- Device operations: `btrfs_init_new_device`, `btrfs_rm_device`, `btrfs_grow_device`, `btrfs_shrink_device`, `btrfs_find_device_by_devspec`, `btrfs_find_device`
- Chunk operations: `btrfs_create_chunk`, `btrfs_chunk_alloc_add_chunk_item`, `btrfs_remove_chunk`, `btrfs_remove_dev_extents`, `btrfs_add_chunk_map`, `btrfs_remove_chunk_map`
- Mapping: `btrfs_map_block`, `btrfs_map_discard`, `btrfs_map_repair_block`, `btrfs_num_copies`, `btrfs_full_stripe_len`
- Balance: `btrfs_balance`, `btrfs_pause_balance`, `btrfs_cancel_balance`, `btrfs_resume_balance_async`, `btrfs_recover_balance`
- Mount loading/validation: `btrfs_read_sys_array`, `btrfs_read_chunk_tree`, `btrfs_verify_dev_extents`, `btrfs_verify_dev_items`, `btrfs_check_rw_degradable`
- Stats: `btrfs_init_dev_stats`, `btrfs_run_dev_stats`, `btrfs_get_dev_stats`, `btrfs_dev_stat_inc_and_print`
- Profile helpers: `btrfs_bg_flags_to_raid_index`, `btrfs_bg_type_to_raid_name`, `btrfs_nr_parity_stripes`, `btrfs_bg_type_to_factor`, `btrfs_describe_block_groups`

## Research Notes

This file is one of the central integration points for Btrfs. It connects block-device discovery, mount assembly, chunk allocation, space accounting, relocation, device replacement, read/write mapping, and persistent metadata updates. The most important invariants to preserve when modifying it are:

- Device list, chunk tree, and system chunk array updates must follow the documented lock ordering.
- Chunk allocation must update in-memory maps, device allocation bits, block groups, device byte counters, and later chunk/device tree items consistently.
- Removal and resize must relocate all affected chunks before shrinking or detaching physical storage.
- Device replace can mutate device identity and must be excluded or synchronized during chunk persistence and I/O mapping.
- Degraded and seed/sprout logic depends on distinguishing fsid, metadata_uuid, device uuid, devid, generation, and per-fs_devices ownership.
- RAID geometry comes from `btrfs_raid_array[]`; changing profile semantics requires auditing allocation, mapping, balance validation, degraded checks, and verification paths together.
