# File Research: sources/local-fs/btrfs-linux/fs/btrfs/volumes.h

This header defines the main public data structures, constants, inline helpers, and declarations for Btrfs multi-device volume management, chunk mapping, RAID geometry, device lookup, device statistics, balance/device operations, and logical-to-physical I/O mapping.

Core constants and RAID definitions:
- `BTRFS_MAX_DATA_CHUNK_SIZE` caps a data chunk at 10 GiB.
- `BTRFS_MAX_DISCARD_CHUNK_SIZE` limits one discard request to 1 GiB.
- `BTRFS_STRIPE_LEN`, `BTRFS_STRIPE_LEN_SHIFT`, and `BTRFS_STRIPE_LEN_MASK` define the 64 KiB Btrfs stripe unit used by chunk mapping, RAID56, and zoned allocation logic.
- `enum btrfs_raid_types` maps on-disk block-group profile bits to internal RAID indexes. Compile-time assertions enforce stable indexes for RAID0, RAID1, DUP, RAID10, RAID5, RAID6, RAID1C3, and RAID1C4.
- `struct btrfs_raid_attr` describes per-profile RAID constraints: minimum/maximum devices, tolerated failures, copies, parity stripes, device increment, and block-group flag.

Main structures:
- `struct btrfs_device` represents one member device. It tracks membership lists, owning `btrfs_fs_devices`, opened block device/file, optional zoned info, state bits, device id, sizes, bytes used, I/O alignment, superblock write errors, flush bio, scrub context, device stats, sysfs kobjects, allocation extent state, and temporary per-profile allocation accounting.
- `struct btrfs_fs_devices` represents the device set for one filesystem UUID. It stores `fsid`, `metadata_uuid`, device counts, opened/missing/rw totals, seed devices, device/allocation lists, sysfs state, mount/open hold counts, feature booleans, chunk allocation policy, mirrored-read policy, and per-profile available-space estimates.
- `struct btrfs_io_stripe` is one mapped physical stripe: target device, physical offset, raid-stripe-tree search flag, and backpointer to its `btrfs_io_context`.
- `struct btrfs_io_context` is the logical-to-physical mapping result used during bio submission. It carries refcounting, map type, original bio, error accounting, logical range, stripe count, selected mirror, device-replace duplication metadata, RAID56 full-stripe logical address, and variable `stripes[]`.
- `struct btrfs_chunk_map` is the in-memory mapping tree node for one logical chunk, with start, length, stripe size, profile type, alignment, stripe count, sub-stripes, verification counter, rb-tree node, refcount, and variable stripe array.
- `struct btrfs_swapfile_pin` records a device or block group pinned by an active swapfile, sorted by pointer and inode to block unsafe operations.
- `struct btrfs_balance_control` stores ioctl balance filters and progress.
- `struct btrfs_dev_lookup_args` centralizes device lookup by devid, uuid, fsid, devt, or missing-device flag.

Important inline helpers:
- `BTRFS_DEVICE_GETSET_FUNCS()` generates accessors for `total_bytes`, `disk_total_bytes`, and `bytes_used`. On 32-bit SMP it uses a seqcount to avoid torn 64-bit reads; on 32-bit preempt kernels it disables preemption; otherwise it reads/writes directly.
- `btrfs_free_chunk_map()` frees a chunk map only after its refcount reaches zero and asserts the rb-node has been removed.
- `btrfs_op()` converts a bio operation into `BTRFS_MAP_READ` or `BTRFS_MAP_WRITE`, treating zone append as write.
- `btrfs_chunk_item_size()` computes the on-disk chunk item size for a stripe count.
- `btrfs_stripe_nr_to_offset()` safely converts a 32-bit stripe number to a 64-bit byte offset.
- Device stat helpers increment, read, reset, and set per-device stats while updating `dev_stats_ccnt` with required memory ordering.
- `btrfs_dev_name()` returns the RCU device name or `"<missing disk>"`.
- `btrfs_fs_devices_inc_holding()` and `btrfs_fs_devices_dec_holding()` require `uuid_mutex` and protect mount-time references before devices are opened.
- `btrfs_get_per_profile_avail()` reads cached per-profile available-space estimates under `per_profile_lock`.

Declared API surface:
- Mapping and bio context: `btrfs_map_block()`, `btrfs_map_repair_block()`, `btrfs_map_discard()`, `btrfs_get_bioc()`, `btrfs_put_bioc()`.
- Chunk tree and mapping tree: `btrfs_read_sys_array()`, `btrfs_read_chunk_tree()`, `btrfs_create_chunk()`, `btrfs_mapping_tree_free()`, `btrfs_find_chunk_map()`, `btrfs_get_chunk_map()`, `btrfs_remove_chunk_map()`, `btrfs_chunk_alloc_add_chunk_item()`, `btrfs_remove_chunk()`, `btrfs_remove_dev_extents()`.
- Device lifecycle: `btrfs_open_devices()`, `btrfs_close_devices()`, `btrfs_scan_one_device()`, `btrfs_forget_devices()`, `btrfs_alloc_device()`, `btrfs_init_new_device()`, `btrfs_rm_device()`, `btrfs_grow_device()`, `btrfs_shrink_device()`, `btrfs_update_device()`.
- Device lookup and identity: `btrfs_find_device()`, `btrfs_find_device_by_devspec()`, `btrfs_get_dev_args_from_path()`, `btrfs_put_dev_args_from_path()`, `btrfs_sb_fsid_ptr()`.
- Balance and relocation: `btrfs_balance()`, `btrfs_resume_balance_async()`, `btrfs_recover_balance()`, `btrfs_pause_balance()`, `btrfs_cancel_balance()`, `btrfs_relocate_chunk()`.
- Device replace helpers: `btrfs_rm_dev_replace_remove_srcdev()`, `btrfs_rm_dev_replace_free_srcdev()`, `btrfs_destroy_dev_replace_tgtdev()`.
- Geometry/profile helpers: `btrfs_full_stripe_len()`, `btrfs_calc_stripe_length()`, `btrfs_nr_parity_stripes()`, `btrfs_bg_flags_to_raid_index()`, `btrfs_bg_type_to_factor()`, `btrfs_bg_type_to_raid_name()`, `btrfs_describe_block_groups()`.
- Verification and repair: `btrfs_verify_dev_extents()`, `btrfs_verify_dev_items()`, `btrfs_check_rw_degradable()`, `btrfs_repair_one_zone()`, `btrfs_scratch_superblocks()`.
- Swapfile/pending extents: `btrfs_pinned_by_swapfile()`, `btrfs_first_pending_extent()`, `btrfs_find_hole_in_pending_extents()`.

Cross-file relationships:
- Implemented mainly by `volumes.c`, with device replace, zoned mode, RAID56, scrub, balance, chunk allocation, disk I/O, sysfs, and transaction code consuming these types.
- `raid56.c` depends on `struct btrfs_io_context`, `BTRFS_STRIPE_LEN`, and RAID profile geometry.
- `zoned.c` depends on `struct btrfs_device`, `struct btrfs_fs_devices`, `struct btrfs_chunk_map`, and stripe geometry for zone allocation and write-pointer recovery.
- `bio.c` and lower I/O submission code consume `btrfs_map_block()` results and `btrfs_io_context`.
- Device stats are exported through ioctl/sysfs-facing paths and persisted by transaction commit helpers.

Important invariants and risks:
- RAID enum indexes are coupled to on-disk block-group profile bits and guarded by static assertions; changing profile bits would break mapping.
- Device size fields need generated accessors outside their natural locking contexts on 32-bit platforms.
- `btrfs_io_context::num_stripes` includes device-replace duplicated stripes, so callers must distinguish real stripes from replacement stripes with `replace_nr_stripes`.
- RAID56 `full_stripe_logical` implies a specific stripe ordering: data stripes first, then P, then Q for RAID6.
- `btrfs_chunk_map` objects must be removed from the rb-tree before the final put.
- Device-stat counter updates rely on memory barriers paired with `btrfs_run_dev_stats()`.
- `fs_devices->holding` is protected by `uuid_mutex`; mount code must not manipulate it locklessly.
- Per-profile available-space estimates can be stale or unavailable and use `U64_MAX` as the sentinel.
