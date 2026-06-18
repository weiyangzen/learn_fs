# File Research: sources/os/linux/linux/fs/nilfs2/sysfs.c

Implements NILFS2 sysfs exposure under `/sys/fs/nilfs2`. It creates the global NILFS kset, the global `features` group, per-device kobjects, device subgroups, and per-mounted-snapshot kobjects.

Main responsibilities:
- Creates `/sys/fs/nilfs2/features` with driver revision and README.
- Creates per-device `/sys/fs/nilfs2/<device>` with attributes for revision, block size, device size, free blocks, UUID, volume name, and README.
- Creates per-device subgroups: `mounted_snapshots`, `checkpoints`, `segments`, `superblock`, and `segctor`.
- Creates snapshot kobjects for current checkpoint and mounted historical snapshots.
- Deletes kobjects with completion-backed release handlers.

Important exposed telemetry:
- Snapshot: `inodes_count`, `blocks_count`.
- Checkpoints: checkpoint count, snapshot count, latest segment checkpoint, next checkpoint.
- Segments: total segments, blocks per segment, clean and dirty segment counts.
- Segment constructor: latest partial segment block, sequence, checkpoint, current/next segment cursor, write times, dirty data blocks.
- Superblock: write time, write count, writable `sb_update_frequency`.
- Device: raw superblock revision, block size, device size, free blocks, UUID, volume name.

Concurrency and correctness:
- Uses `ns_sem` for superblock/shared state.
- Uses `ns_segctor_sem` for segment-constructor state.
- Uses `ns_last_segment_lock` for last-written-segment cursor fields.
- Reads metadata file stats through `nilfs_cpfile_get_stat()` and `nilfs_sufile_get_stat()` under appropriate locks.
- `sb_update_frequency` parsing uses `kstrtouint(skip_spaces(...))` and clamps values below `NILFS_SB_FREQ` to 10 seconds.

Dependencies:
- `nilfs.h`, `mdt.h`, `sufile.h`, `cpfile.h`, `sysfs.h`.
- Runtime state from `struct the_nilfs` and `struct nilfs_root`.
- Kernel sysfs/kobject APIs.

Risk notes:
- `nilfs_dev_volume_name_show()` uses `scnprintf(buf, sizeof(raw_sb->s_volume_name), "%s\n", ...)`, so the sysfs output bound is the raw field size, not PAGE_SIZE. This is intentional-looking but unusual.
- Most attributes are read-only. The only mutating sysfs path in this file is `superblock/sb_update_frequency`.
- Kobject deletion uses `kobject_put()` for subgroups but does not explicitly wait on the completion fields in this file; lifecycle safety depends on broader NILFS teardown ordering.
