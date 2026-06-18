# File Research: sources/local-fs/btrfs-linux/fs/btrfs/raid56.c

This file implements Btrfs RAID5/RAID6 parity I/O: write read-modify-write, failed-read reconstruction, parity scrub/repair, device-replace duplication, stripe locking, stripe caching, and rbio lifecycle. Its main exported entry points are `raid56_parity_write()`, `raid56_parity_recover()`, `raid56_parity_alloc_scrub_rbio()`, `raid56_parity_submit_scrub_rbio()`, `raid56_parity_cache_data_folios()`, `btrfs_alloc_stripe_hash_table()`, and `btrfs_free_stripe_hash_table()`.

Core private state:
- `struct btrfs_stripe_hash_table` owns the stripe hash buckets, LRU cache list, cache lock, and cache size.
- `struct btrfs_stripe_hash` is one hash bucket with a stripe list and lock.
- `struct btrfs_raid_bio` comes from `raid56.h` and represents one full RAID56 stripe, including all data and P/Q stripes.
- Per-rbio arrays map logical sectors to physical addresses: `bio_paddrs` for caller bios and `stripe_paddrs`/`stripe_pages` for internally allocated read/parity/recovery pages.
- Bitmaps track partial-write data columns (`dbitmap`), sector errors (`error_bitmap`), valid internal stripe sectors (`stripe_uptodate_bitmap`), temporary parity scrub sectors (`finish_pbitmap`), and optional data checksum coverage (`csum_bitmap`).

Stripe locking and caching:
- `btrfs_alloc_stripe_hash_table()` allocates a hash table of `1 << BTRFS_STRIPE_HASH_TABLE_BITS` buckets and initializes the LRU cache.
- `lock_stripe_add()` serializes all rbios for the same full-stripe logical address. It either gives the caller ownership, merges compatible rbios, queues an rbio on the current owner’s plug list, or steals cached data pages from an idle cached rbio.
- `unlock_stripe()` releases ownership, optionally keeps a cache-only rbio in the hash, or hands the stripe to the next pending rbio and schedules its operation-specific worker.
- `cache_rbio_pages()`, `cache_rbio()`, `steal_rbio()`, `remove_rbio_from_cache()`, and `btrfs_clear_rbio_cache()` implement a small LRU cache of full-stripe data sectors. Cached rbios are used to avoid rereading data sectors for later partial writes.
- `RBIO_RMW_LOCKED_BIT` prevents late merge once final RMW assembly starts; `RBIO_CACHE_BIT` marks cache ownership; `RBIO_CACHE_READY_BIT` says cached `stripe_pages` can be trusted.

Rbio allocation and indexing:
- `alloc_rbio()` derives geometry from `btrfs_io_context`: real stripes exclude replace target stripes, `nr_data` excludes parity stripes, stripe length is fixed at `BTRFS_STRIPE_LEN`, and sectors can have multiple steps when filesystem block size exceeds page size.
- `alloc_rbio_pages()`, `alloc_rbio_data_pages()`, `alloc_rbio_parity_pages()`, `alloc_rbio_sector_pages()`, and `alloc_rbio_essential_pages()` allocate only the page ranges needed by each path.
- `index_rbio_pages()` indexes higher-layer bio segments into `bio_paddrs`; `index_stripe_sectors()` indexes internally allocated pages into `stripe_paddrs`.
- Helpers such as `rbio_sector_index()`, `rbio_paddr_index()`, `sector_paddrs_in_rbio()`, and `sector_paddr_in_rbio()` centralize stripe/sector/step address lookup.

Write path:
- `raid56_parity_write()` wraps a higher-layer write bio in a `BTRFS_RBIO_WRITE` rbio, marks covered data columns in `dbitmap`, and either plugs partial writes or immediately schedules RMW work.
- `raid_unplug()` sorts plugged rbios by logical sector and merges compatible partial writes before dispatching them to `rmw_rbio_work()`.
- `rmw_rbio()` allocates parity pages, reads missing data sectors for sub-stripe writes when the cache is insufficient, verifies checksummed data during the read phase, reconstructs bad sectors when possible, marks the rbio RMW-locked, generates P/Q for every vertical stripe, assembles write bios, submits them, waits for completion, and completes original bios.
- Full-stripe writes skip reading data sectors and generally do not populate the stripe cache; partial writes can cache the resulting full data stripe.
- `rmw_assemble_write_bios()` writes updated caller data sectors plus generated parity sectors. During device replace it duplicates the source stripe to the replace target stripe.

Failed-read recovery:
- `raid56_parity_recover()` handles failed normal reads from `bio.c`. It wraps the failed bio as `BTRFS_RBIO_READ_REBUILD`, records the failed sector range, optionally marks an extra failed stripe for RAID6 mirror retries, and schedules `recover_rbio_work()`.
- `recover_rbio()` allocates the full stripe, rereads all nonfailed sectors without trusting cache contents, then calls `recover_sectors()`.
- `recover_vertical_step()` performs RAID5 XOR recovery, RAID6 single-failure recovery, or RAID6 two-data/data+parity recovery with `raid6_datap_recov()` / `raid6_2data_recov()`.
- `recover_vertical()` checks the vertical stripe’s error count against `bioc->max_errors`, reconstructs failed sectors, verifies recovered data checksums when available, and marks recovered sectors uptodate.
- `set_rbio_raid6_extra_error()` implements retry behavior for RAID6 mirror numbers greater than 2 by selecting another stripe to treat as failed.

Checksum handling:
- `fill_data_csums()` loads checksums for the data portion of a full stripe before RMW reads, except for metadata and mixed block groups to avoid recursive RAID56 recovery deadlocks while holding a full-stripe lock.
- `verify_bio_data_sectors()` verifies read sectors against `csum_buf` during RMW reads.
- `verify_one_sector()` verifies a reconstructed data sector before it is accepted.
- If checksum lookup allocation or search fails, the code warns that sub-stripe write safety is degraded and proceeds without checksum verification.

Parity scrub and replace:
- `raid56_parity_alloc_scrub_rbio()` builds a `BTRFS_RBIO_PARITY_SCRUB` rbio around scrub’s completion bio, records which parity stripe is being scrubbed, and copies the caller’s horizontal-sector bitmap.
- `raid56_parity_cache_data_folios()` lets scrub prefill data stripe pages from already verified folios so the parity path can avoid extra reads.
- `raid56_parity_submit_scrub_rbio()` serializes the scrub rbio through the same stripe lock as writes and recovery.
- `scrub_rbio()` allocates only needed sectors, reads missing inputs, recovers tolerable data failures, verifies or repairs parity sectors, writes repaired parity, and waits for write completion.
- `finish_parity_scrub()` compares generated P/Q against the scrubbed parity stripe, clears `dbitmap` bits that already matched, writes only repaired sectors, and duplicates the parity write to the replace target when appropriate.
- `recover_scrub_rbio()` is stricter than ordinary recovery because the parity stripe being scrubbed cannot always be used as a trusted recovery source.

Bio submission and completion:
- `rbio_add_io_paddrs()` builds physical-device bios for one sector and merges adjacent sectors on the same block device when possible. Missing devices set error bits and can fail early if tolerance is exceeded.
- `submit_read_wait_bio_list()` and `submit_write_bios()` install RAID56-specific endio callbacks, emit trace events, submit bios, and synchronize using `stripes_pending` plus `io_wait`.
- `raid_wait_read_end_io()` records I/O errors or marks read pages uptodate and checksum-verifies data sectors.
- `raid_wait_write_end_io()` records write errors.
- `rbio_orig_end_io()` frees checksum state, clears the data bitmap before unlocking, releases stripe ownership/cache references, frees the rbio, and completes all original bios with the final status.

Cross-file relationships:
- `bio.c` calls `raid56_parity_write()` for RAID56 writes and `raid56_parity_recover()` when normal reads need parity reconstruction.
- `scrub.c` allocates, optionally preloads, and submits scrub rbios through the scrub entry points.
- `disk-io.c` initializes and frees the stripe hash table during filesystem mount/unmount lifecycle.
- `volumes.c`, `block-group.c`, and `scrub.c` use RAID56 geometry helpers declared in `raid56.h`, especially `nr_data_stripes()`.
- The implementation depends on `volumes.h` for `btrfs_io_context`, `file-item.h` for checksum lookup/calculation, `async-thread.h` for the RMW worker pool, and the kernel RAID6/XOR libraries for parity math.

Important invariants and risks:
- Only one active rbio may own a full stripe while RMW, read recovery, or scrub repair is in progress; merge and cache decisions depend on `RBIO_RMW_LOCKED_BIT`, `bio_list_lock`, and the stripe hash bucket lock.
- `bio_paddrs` and `stripe_paddrs` must be reindexed after page allocation or page stealing, especially for block-size-greater-than-page-size configurations.
- Partial writes are unsafe without correct pre-write data contents; the code mitigates this with checksum lookup, data-sector reads, cache validation, and recovery before parity generation.
- Missing devices and checksum mismatches share `error_bitmap`; per-vertical-stripe error counts must never exceed `bioc->max_errors`.
- Device replace makes `bioc->num_stripes` larger than `real_stripes`, so write assembly checks target stripe numbers against `bioc->num_stripes`, not only `real_stripes`.
- Metadata or mixed-block-group checksum lookup is deliberately skipped to avoid deadlocking on recursive RAID56 recovery while the stripe lock is held.
- Scrub repair has lower data-recovery capability when the scrubbed parity stripe is one of the failed inputs.
