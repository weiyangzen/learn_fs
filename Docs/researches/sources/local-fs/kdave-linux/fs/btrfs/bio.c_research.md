# File Research: sources/local-fs/kdave-linux/fs/btrfs/bio.c

Purpose: Implements Btrfs high-level bio allocation, submission, splitting, checksum handling, read repair, mirrored/RAID56 mapping, zone append handling, repair writes, and bioset lifecycle.

Core objects:
- `btrfs_bioset`: main `struct btrfs_bio` bioset.
- `btrfs_clone_bioset`: split/clone bioset.
- `btrfs_repair_bioset`: repair-read bioset.
- `btrfs_failed_bio_pool`: mempool for tracking failed read repairs.
- `struct btrfs_failed_bio`: original failed bio, number of mirror copies, and outstanding repair count.

Allocation and completion:
- `btrfs_bio_init()` initializes the Btrfs wrapper fields while leaving the embedded block-layer bio intact.
- `btrfs_bio_alloc()` allocates from the main bioset and initializes wrapper state.
- `btrfs_split_bio()` splits an original bio at a map boundary, propagates inode/file offset/checksum/ordered extent flags, and increments original pending I/O count.
- `btrfs_bio_end_io()` waits for async checksum completion when needed, folds clone completion into the original bio, preserves the first error status, decrements pending split I/O count, calls the upper end I/O once, and drops ordered extent refs.

Read checksum and repair:
- `btrfs_check_read_bio()` verifies data checksums sector by sector and starts repair reads for failed sectors or device errors.
- `repair_one_sector()` submits a one-sector repair read to the next mirror when copies exist.
- `btrfs_end_repair_bio()` checks the repair read, rotates through mirrors if needed, and writes good data back to bad mirrors through `btrfs_repair_io_failure()`.
- `btrfs_repair_io_failure()` maps a specific bad mirror and performs a synchronous repair write if the filesystem is writable and zone repair rules allow it.

I/O submission:
- `btrfs_submit_bbio()` asserts alignment and loops through `btrfs_submit_chunk()` until the full bio range is mapped/submitted.
- `btrfs_submit_chunk()` maps logical to physical stripes, splits bios at map or zone append boundaries, preloads read checksums, decides write checksum behavior, attaches RAID stripe tree bioc information for ordered extents, and submits or ends with error.
- `btrfs_submit_bio()` dispatches to the single-mirror fast path, RAID56 parity paths, or mirrored-write fanout.
- `btrfs_submit_dev_bio()` validates device presence/writeability, handles zone append sector rewrites, updates read stats, and submits directly or through `blkcg_punt_bio_submit`.

Write behavior:
- `btrfs_bio_csum()` computes metadata or data checksums; data checksum behavior changes under `CONFIG_BTRFS_EXPERIMENTAL`.
- `should_async_write()` chooses async checksum submission unless checksums are fast, I/O is synchronous, metadata on zoned devices requires ordering, or experimental mode disables this path.
- `btrfs_wq_submit_bio()` queues checksum and later submission through Btrfs workers.
- NODATASUM, no-data-csum state, data relocation roots, and remapped data can bypass normal data checksum generation; zoned cases may allocate dummy sums.

Completion paths:
- `btrfs_simple_end_io()` handles single-stripe I/O and queues task-context end I/O work.
- `btrfs_raid56_end_io()` handles RAID56 completion already in task context.
- `btrfs_orig_write_end_io()` and clone write completion aggregate mirrored write errors through `bioc->error`, tolerate failures up to `max_errors`, record zone append physical sectors, and release bioc state.

Repair and scrub:
- `btrfs_submit_repair_write()` submits a mapped metadata repair write to one mirror and can redirect to the dev-replace target.
- Repair write intentionally bypasses `btrfs_submit_bbio()` because it must not write all mirrors.

Initialization:
- `btrfs_bioset_init()` initializes all biosets and the failed-bio mempool, unwinding through `btrfs_bioset_exit()` on failure.
- `btrfs_bioset_exit()` releases the mempool and biosets.

Error handling and invariants:
- Device I/O errors update per-device read/write/flush stats with rate-limited warnings for unexpected statuses.
- Many paths assert task context, sector/page alignment, non-null inode, mirror number, metadata/data constraints, and sufficient bio vec space.
- Mapping or checksum failures end the current and any remaining split bio exactly once.

Risk notes: This file is central to data integrity. Subtle areas include split bio pending accounting, ordered extent ref ownership, async checksum lifetime, repair mirror rotation, zone append length/alignment, RAID error tolerance, and ensuring end I/O always runs in task context.
