# File Research: sources/os/linux/linux/fs/btrfs/bio.c

Purpose: Implements Btrfs bio allocation, splitting, submission, end I/O handling, data checksum verification, read repair, mirrored/RAID56 I/O dispatch, async write checksumming, zoned append handling, and bioset lifecycle.

Main state:
- `btrfs_bioset`: primary `struct btrfs_bio` allocation pool.
- `btrfs_clone_bioset`: pool for split/clone bios.
- `btrfs_repair_bioset`: pool for repair reads.
- `btrfs_failed_bio_pool`: mempool of `struct btrfs_failed_bio` tracking repair state.

Bio setup and completion:
- `btrfs_bio_init()` initializes Btrfs-specific fields around an embedded block-layer bio.
- `btrfs_bio_alloc()` allocates from the Btrfs bioset and initializes the wrapper.
- `btrfs_split_bio()` splits bios at mapping boundaries, propagating inode, offsets, ordered extent references, checksum mode, scrub/remap flags, and async checksum state.
- `btrfs_bio_end_io()` joins split completions back to the original bio, preserves the first error, waits for async checksums when needed, drops ordered extent refs, and invokes the caller endio callback.

Read checksumming and repair:
- `btrfs_check_read_bio()` verifies data read checksums sector by sector.
- Bad sectors trigger `repair_one_sector()`, which reads from alternate mirrors and tracks outstanding repair attempts through `struct btrfs_failed_bio`.
- `btrfs_end_repair_bio()` checks the repair read, retries additional mirrors if needed, and writes good data back to failed mirrors with `btrfs_repair_io_failure()`.
- Repair uses page/sector stepping to support block sizes larger than page size.

Device error reporting:
- `btrfs_log_dev_io_error()` records read/write/flush errors in device stats and rate-limits unexpected status warnings.
- Read-ahead errors do not increment read error stats.

End I/O workqueues:
- `btrfs_simple_end_io()` decrements the bio counter, logs errors, and queues task-context endio work.
- `simple_end_io_work()` handles data read checksum/repair, metadata read completion, zone append physical recording, and final completion.
- RAID56 endio is handled in task context by `btrfs_raid56_end_io()`.
- Mirrored write completions use separate original and clone endio work functions to aggregate errors against the mirror tolerance threshold.

Submission path:
- `btrfs_submit_dev_bio()` validates target device presence/writeability, sets the block device, transforms eligible writes into zone append writes, records stats, and either punts cgroup submission or calls `submit_bio()`.
- `btrfs_submit_bio()` dispatches a mapped bio to the single-mirror fast path, RAID56 parity path, or mirrored write fanout.
- `btrfs_submit_mirrored_bio()` clones bios for all but the last mirror and submits each stripe.

Checksumming and async submission:
- `btrfs_bio_csum()` computes metadata or data checksums; experimental builds pass a different data checksum mode.
- `async_submit_bio` wraps a bio, mapping context, stripe map, mirror number, and Btrfs work item.
- `run_one_async_start()` computes checksums in worker context.
- `run_one_async_done()` either completes on checksum error or marks `REQ_BTRFS_CGROUP_PUNT` and submits the bio.
- `should_async_write()` avoids async checksumming for experimental mode, fast checksum implementations, synchronous I/O, and zoned metadata writes.
- `btrfs_wq_submit_bio()` allocates async work and queues it on `fs_info->workers`.

Chunk mapping:
- `btrfs_submit_chunk()` maps a logical range with `btrfs_map_block()`, handles data-read checksum preloading, splits at map or zone-append boundaries, records original logical addresses for data writes, attaches raid-stripe-tree ordered contexts, computes or allocates checksums, and submits the mapped bio.
- `btrfs_submit_bbio()` asserts alignment and repeatedly submits chunks until the full bio is consumed.

Repair writes:
- `btrfs_repair_io_failure()` bypasses normal multi-copy submission to write one bad mirror synchronously, with read-only and zoned-repair checks.
- `btrfs_submit_repair_write()` submits metadata scrub repair writes, optionally redirecting to the device-replace target.

Lifecycle:
- `btrfs_bioset_init()` initializes all biosets and the failed-bio mempool.
- `btrfs_bioset_exit()` tears them down in reverse order.

Risk notes: This file coordinates block-layer lifetime, Btrfs ordered extents, checksum state, device replacement, RAID profiles, zoned append semantics, and read repair. The most sensitive areas are split-bio completion accounting, ordered extent reference ownership, checksum/repair iteration for block-size-greater-than-page-size cases, and bypass paths that intentionally avoid normal multi-mirror submission.
