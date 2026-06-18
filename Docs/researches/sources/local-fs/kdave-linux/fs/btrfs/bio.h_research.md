# File Research: sources/local-fs/kdave-linux/fs/btrfs/bio.h

Purpose: Defines the `struct btrfs_bio` high-level I/O wrapper and declares the Btrfs bio API.

Main structure:
- `struct btrfs_bio` embeds a block-layer `struct bio` as its last member.
- Tracks target inode and file offset for data I/O.
- Uses a union for data read checksum state, data write ordered/checksum/original-address state, or metadata read parent-check state.
- Stores `end_io_work`, upper completion callback/private pointer, pending split I/O count, selected mirror number, first error status, and feature flags.

Flags and fields:
- `csum_search_commit_root`: read checksums from commit root for data reads.
- `is_scrub`: distinguishes scrub use of the btree inode.
- `is_remap`: identifies remapped data I/O.
- `async_csum`: write checksum generation is asynchronous.
- `can_use_append`: eligible for zone append.
- `BTRFS_BIO_INLINE_CSUM_SIZE` provides small inline checksum storage.

Public API:
- `btrfs_bio()` converts embedded `struct bio *` to wrapper.
- Bioset lifecycle: `btrfs_bioset_init()` and `btrfs_bioset_exit()`.
- Allocation/init/completion: `btrfs_bio_init()`, `btrfs_bio_alloc()`, `btrfs_bio_end_io()`.
- Submission and repair: `btrfs_submit_bbio()`, `btrfs_submit_repair_write()`, `btrfs_repair_io_failure()`.
- `REQ_BTRFS_CGROUP_PUNT` maps to `REQ_FS_PRIVATE` for cgroup-aware deferred submission.

Integration: Consumed by `bio.c` and by Btrfs read/write, metadata, scrub, direct I/O, file-item checksum, zoned, RAID, and repair paths.

Risk notes: The embedded `bio` must remain last because `bio_alloc_bioset()` allocates enough bytes for the wrapper by offset. Callers must populate `inode` for normal submit paths because checksum, mapping, workqueue, and fs_info access depend on it.
