# File Research: sources/os/linux/linux-stable/fs/nilfs2/sysfs.c

## Purpose
Implements NILFS2 sysfs support under `/sys/fs/nilfs2`. It exposes global driver features, per-device metadata, mounted snapshot counters, checkpoint statistics, segment statistics, segment-constructor state, and superblock update state.

## Main Interfaces
- Global lifecycle:
  - `nilfs_sysfs_init()` creates the `nilfs2` kset under `fs_kobj` and the global `features` group.
  - `nilfs_sysfs_exit()` removes the feature group and unregisters the kset.
- Device lifecycle:
  - `nilfs_sysfs_create_device_group(struct super_block *sb)` allocates `nilfs_sysfs_dev_subgroups`, creates `/sys/fs/nilfs2/<device>`, then creates child groups.
  - `nilfs_sysfs_delete_device_group(struct the_nilfs *nilfs)` removes child groups, deletes/puts the device kobject, and frees subgroup storage.
- Snapshot lifecycle:
  - `nilfs_sysfs_create_snapshot_group(struct nilfs_root *root)` creates either `current_checkpoint` or `mounted_snapshots/<cno>`.
  - `nilfs_sysfs_delete_snapshot_group(struct nilfs_root *root)` puts the snapshot kobject.

## Sysfs Layout
- `/sys/fs/nilfs2/features`
  - `revision`
  - `README`
- `/sys/fs/nilfs2/<device>`
  - `revision`
  - `blocksize`
  - `device_size`
  - `free_blocks`
  - `uuid`
  - `volume_name`
  - `README`
- `/sys/fs/nilfs2/<device>/mounted_snapshots`
  - `README`
- `/sys/fs/nilfs2/<device>/mounted_snapshots/<cno>` or `/sys/fs/nilfs2/<device>/current_checkpoint`
  - `inodes_count`
  - `blocks_count`
  - `README`
- `/sys/fs/nilfs2/<device>/checkpoints`
  - `checkpoints_number`
  - `snapshots_number`
  - `last_seg_checkpoint`
  - `next_checkpoint`
  - `README`
- `/sys/fs/nilfs2/<device>/segments`
  - `segments_number`
  - `blocks_per_segment`
  - `clean_segments`
  - `dirty_segments`
  - `README`
- `/sys/fs/nilfs2/<device>/segctor`
  - `last_pseg_block`
  - `last_seg_sequence`
  - `last_seg_checkpoint`
  - `current_seg_sequence`
  - `current_last_full_seg`
  - `next_full_seg`
  - `next_pseg_offset`
  - `next_checkpoint`
  - `last_seg_write_time`
  - `last_seg_write_time_secs`
  - `last_nongc_write_time`
  - `last_nongc_write_time_secs`
  - `dirty_data_blocks_count`
  - `README`
- `/sys/fs/nilfs2/<device>/superblock`
  - `sb_write_time`
  - `sb_write_time_secs`
  - `sb_write_count`
  - `sb_update_frequency`
  - `README`

## Implementation Notes
The file uses macros to generate common `show`, `store`, `kobj_type`, release, create, and delete code for device child groups. Each group has typed attribute wrappers declared in `sysfs.h`, so callbacks receive either `struct the_nilfs *` or `struct nilfs_root *`.

Most attributes are read-only. `superblock/sb_update_frequency` is read-write; store parsing uses `kstrtouint(skip_spaces(buf), 0, &val)`, clamps values below `NILFS_SB_FREQ` to the 10-second minimum, and updates `nilfs->ns_sb_update_freq` under `ns_sem`.

## Locking and State Access
- `ns_segctor_sem` protects live segment-constructor fields and metadata file stats.
- `ns_last_segment_lock` protects last segment cursor fields exposed by checkpoint/segctor attributes.
- `ns_sem` protects superblock-backed fields such as revision, device size, UUID, volume name, write time, write count, and update frequency.
- Snapshot counters are atomic64 values on `struct nilfs_root`.
- Dirty block count is read from `ns_ndirtyblks`.

## Dependencies
Includes `nilfs.h`, `mdt.h`, `sufile.h`, `cpfile.h`, and `sysfs.h`. Calls into checkpoint and segment usage metadata helpers:
- `nilfs_cpfile_get_stat()`
- `nilfs_sufile_get_stat()`
- `nilfs_sufile_get_ncleansegs()`
- `nilfs_count_free_blocks()`

## Error Handling
Device group creation unwinds in reverse order on partial failure. On kobject init failures, the relevant kobject is put. Feature group creation failure unregisters the global kset. Attribute callbacks log NILFS errors when metadata stat retrieval or string parsing fails.

## Research Notes
This file is an observability/control surface for NILFS2 rather than core allocation logic. Its correctness depends on matching sysfs kobject lifetime to `the_nilfs` and `nilfs_root` lifetimes, and on using the same locks as writers of the exposed fields.
