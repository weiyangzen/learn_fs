# File Research: sources/os/linux/linux/fs/btrfs/volumes.h

## Purpose
Defines the core Btrfs multi-device, chunk mapping, RAID profile, device-statistics, balance, and physical I/O mapping interfaces. This header is the shared contract between chunk allocation/removal, device open/scan/replace/remove, logical-to-physical bio mapping, degraded mount checks, discard mapping, zoned-device support, and user-visible device statistics.

## Main Data Structures
- `struct btrfs_device`: per-device runtime state, including device identity, opened block device/file, zone info, size/usage counters, flush bio, scrub state, device error counters, sysfs kobject, allocation extent tree, and active state bits.
- `struct btrfs_fs_devices`: device set for a filesystem FSID, including device lists, seed devices, open/missing/rw device counts, metadata UUID, allocation/read policy, per-profile available-space cache, and sysfs objects.
- `struct btrfs_io_context`: logical I/O mapping result used during bio submission. It owns stripes, mirror number, replacement-stripe metadata, full-stripe logical address for RAID56, error accounting, and an original bio pointer.
- `struct btrfs_chunk_map`: in-memory logical chunk map with chunk start/length, profile flags, stripe geometry, and physical stripes.
- `struct btrfs_raid_attr`: static RAID profile metadata such as min/max devices, tolerated failures, copies/parity, increment, name, and block-group flag.
- `struct btrfs_swapfile_pin`: rb-tree entry used to pin devices or block groups that contain active swapfile extents.
- `struct btrfs_balance_control`: balance filters and progress for data/metadata/system relocation.

## Constants and Profile Mapping
- `BTRFS_STRIPE_LEN` is fixed at 64 KiB with compile-time checks.
- `BTRFS_MAX_DATA_CHUNK_SIZE` is 10 GiB.
- `BTRFS_MAX_DISCARD_CHUNK_SIZE` caps a single discard request at 1 GiB.
- `enum btrfs_raid_types` maps on-disk block-group profile bits to compact RAID indices; several `static_assert`s protect this ABI-sensitive conversion.
- `BTRFS_RAID1_MAX_MIRRORS` is 4, matching RAID1C4.
- `BTRFS_MAX_DEVS()` and `BTRFS_MAX_DEVS_SYS_CHUNK` derive the maximum stripes storable in chunk items.

## Device State and Statistics
Device state bits record writability, presence in filesystem metadata, missing/replacement-target state, flush state, read-ahead disablement, and whether the device item was found in the chunk tree.

On 32-bit SMP or preemptible configurations, generated accessors for `total_bytes`, `disk_total_bytes`, and `bytes_used` avoid torn 64-bit reads using seqcount or preemption disabling. Device stats are atomic counters with explicit memory ordering around the change counter so transaction-time persistence sees consistent updates.

## Mapping and I/O Interfaces
Key exported APIs:
- `btrfs_map_block()`: maps logical ranges for read/write/get-read-mirrors into physical stripes and optional `btrfs_io_context`.
- `btrfs_map_repair_block()`: maps a selected repair mirror.
- `btrfs_map_discard()`: maps logical discard to physical discard stripes.
- `btrfs_num_copies()`, `btrfs_full_stripe_len()`, `btrfs_calc_stripe_length()`, `btrfs_nr_parity_stripes()`: profile geometry helpers.
- `btrfs_get_bioc()` / `btrfs_put_bioc()`: lifetime management for I/O contexts.

`btrfs_op()` maps Linux bio operations to Btrfs map operations. Writes and zone appends become `BTRFS_MAP_WRITE`; reads become `BTRFS_MAP_READ`.

## Device and Chunk Lifecycle APIs
The header declares mount/device discovery and teardown:
- `btrfs_scan_one_device()`, `btrfs_open_devices()`, `btrfs_close_devices()`, `btrfs_forget_devices()`, `btrfs_free_extra_devids()`.
- `btrfs_alloc_device()`, `btrfs_find_device()`, `btrfs_find_device_by_devspec()`, device lookup-argument helpers, and remove/grow/shrink/init-new-device operations.
- `btrfs_read_sys_array()`, `btrfs_read_chunk_tree()`, `btrfs_create_chunk()`, `btrfs_chunk_alloc_add_chunk_item()`, `btrfs_remove_chunk()`, and `btrfs_remove_dev_extents()`.

Chunk-map APIs provide rb-tree lookup and mutation:
- `btrfs_find_chunk_map()`
- `btrfs_find_chunk_map_nolock()`
- `btrfs_get_chunk_map()`
- `btrfs_remove_chunk_map()`
- `btrfs_mapping_tree_free()`

## Balance, Replacement, and Degraded Operation
Balance entry points include `btrfs_balance()`, async resume/recovery, pause, cancel, and `btrfs_relocate_chunk()`. Device replacement cleanup APIs handle source and target device teardown. Degraded-mode safety is exposed through `btrfs_check_rw_degradable()` and chunk writability through `btrfs_chunk_writeable()`.

## Zoned and Swapfile Integration
`volumes.h` includes cross-file hooks for zoned repair and allocation:
- `btrfs_repair_one_zone()`
- pending extent lookup helpers
- hole lookup in pending extents
- zone-aware device state through `struct btrfs_zoned_device_info *zone_info`

Swapfile pins protect devices or block groups from unsafe relocation/removal while swap is active.

## Concurrency Notes
- `uuid_mutex` protects global filesystem UUID/device-set handling and is asserted by holding-counter helpers.
- `device_list_mutex` protects the full device list.
- `chunk_mutex` protects allocation lists and committed device sizes.
- `per_profile_lock` protects per-profile available-space cache.
- Atomic stats and explicit memory barriers protect device-stat persistence.

## Risk and Testing Signals
Important test coverage should include:
- RAID profile bit-to-index stability.
- 32-bit-safe device size/stat accessors.
- Degraded read/write eligibility.
- Logical-to-physical mapping for mirrored, striped, replacement, and RAID56 profiles.
- Device replacement stripe duplication.
- Chunk map reference lifetime and rb-tree removal.
- Swapfile pin blocking of device/block-group operations.
- Zoned-device repair and pending-extent accounting.
