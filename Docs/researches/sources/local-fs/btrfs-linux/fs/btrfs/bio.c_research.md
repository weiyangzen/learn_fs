# File Research: sources/local-fs/btrfs-linux/fs/btrfs/bio.c

Implements Btrfs bio allocation, mapping, submission, completion, checksum handling, read repair, mirrored writes, RAID56 submission hooks, zone append handling, and bioset lifecycle.

Key points:
- Defines biosets for normal Btrfs bios, cloned bios, repair bios, and a mempool for failed-bio repair state.
- `btrfs_bio_init()` initializes the Btrfs wrapper fields around an already initialized embedded `bio`.
- `btrfs_bio_alloc()` allocates from `btrfs_bioset`; allocation is backed by mempool behavior.
- `btrfs_split_bio()` splits a bio at chunk/map boundaries and preserves Btrfs wrapper state, including ordered extents, checksum flags, scrub/remap flags, async csum mode, and zone append capability.
- `btrfs_bio_end_io()` joins split-bio completion, waits for async checksums when needed, records first error status, releases ordered extents, and calls the original completion callback once all child I/Os finish.
- Read checksum/repair:
  - `btrfs_check_read_bio()` validates data checksums sector by sector.
  - On checksum or I/O failure, `repair_one_sector()` submits a read from another mirror.
  - `btrfs_end_repair_bio()` validates repair reads, tries alternate mirrors if needed, and writes good data back to bad mirrors using `btrfs_repair_io_failure()`.
- Device error accounting:
  - `btrfs_log_dev_io_error()` increments read/write/flush device stats for relevant block statuses.
- Completion handling:
  - `btrfs_simple_end_io()` queues completion work for normal single-device I/O.
  - `btrfs_raid56_end_io()` handles RAID56 parity completion.
  - Mirrored write completions aggregate errors against the tolerated mirror threshold.
- Submission:
  - `btrfs_submit_dev_bio()` validates devices, sets block device, converts writes to zone append on sequential zones when allowed, updates read stats, and submits through cgroup punt or normal `submit_bio()`.
  - `btrfs_submit_mirrored_bio()` clones write bios across mirrors, reusing the original bio for the final mirror.
  - `btrfs_submit_bio()` dispatches to single-mirror, RAID56, or mirrored-write paths.
- Checksumming:
  - `btrfs_bio_csum()` dispatches to metadata or data checksum generation.
  - `should_async_write()` chooses whether to offload data checksum generation to Btrfs workers.
  - Async checksum submission uses `struct async_submit_bio` and ordered Btrfs work callbacks.
- Chunk mapping:
  - `btrfs_submit_chunk()` maps logical bio ranges through `btrfs_map_block()`, splits bios when map length is smaller than bio length, preloads read checksums, prepares write checksums or dummy sums, handles raid-stripe-tree association, and submits the mapped bio.
  - `btrfs_append_map_length()` caps and aligns zone-append writes.
- `btrfs_submit_bbio()` asserts alignment and loops over chunks until the full bio is submitted.
- Repair writes:
  - `btrfs_repair_io_failure()` writes a corrected block to a specific mirror, bypassing normal mirrored write submission.
  - `btrfs_submit_repair_write()` maps and submits scrub/metadata repair writes, optionally redirecting to a device-replace target.
- Bioset lifecycle:
  - `btrfs_bioset_init()` initializes all biosets and failed-bio mempool.
  - `btrfs_bioset_exit()` tears them down in reverse order.

Role in system:
- This is the main Btrfs I/O submission and completion layer between logical filesystem bios and physical devices.
- It is responsible for preserving Btrfs semantics across chunk boundaries, redundancy profiles, checksums, read repair, device replacement, zoned storage, and cgroup-aware submission.
