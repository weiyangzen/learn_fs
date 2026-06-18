# File Research: sources/os/linux/linux/fs/btrfs/raid56.c

## Scope

`raid56.c` implements Btrfs RAID5/RAID6 parity I/O: read-modify-write parity writes, failed-read reconstruction, parity scrub/repair, stripe locking, full-stripe write merging, rbio caching, and device-replace write duplication.

The central object is `struct btrfs_raid_bio`, representing one full RAID56 stripe including data and P/Q parity stripes.

## Main APIs

- `btrfs_alloc_stripe_hash_table()` / `btrfs_free_stripe_hash_table()` allocate and tear down the per-filesystem stripe hash/cache table.
- `raid56_parity_write()` is the write entry point for RAID56 mapped bios.
- `raid56_parity_recover()` rebuilds a failed read from parity.
- `raid56_parity_alloc_scrub_rbio()` creates a parity scrub rbio.
- `raid56_parity_submit_scrub_rbio()` submits scrub/repair work.
- `raid56_parity_cache_data_folios()` preloads known-good scrub data folios into rbio private pages.

## Stripe Locking And Cache

The file uses a hash table keyed by `full_stripe_logical` to serialize operations on a full stripe. `lock_stripe_add()` either grants the stripe lock, merges compatible rbios, queues an rbio on the current owner’s plug list, or steals cached stripe pages from an idle cached rbio.

`unlock_stripe()` releases ownership, optionally keeps an rbio in the cache, or hands the lock to a queued rbio and schedules the correct worker.

The rbio cache stores recently read full-stripe data pages for future sub-stripe writes. Cached rbios are LRU-pruned by `RBIO_CACHE_SIZE`; only data pages are stolen because parity is regenerated.

## Rbio Layout And Indexing

`alloc_rbio()` sizes the rbio from the mapped `btrfs_io_context`: real stripes, data stripes, stripe sectors, stripe pages, and sector steps. It supports both block-size <= page-size and block-size > page-size cases by addressing each filesystem sector as one or more physical-address steps.

Important arrays:

- `bio_paddrs`: physical addresses from higher-level bios.
- `stripe_pages`: private pages allocated for data/parity reads and writes.
- `stripe_paddrs`: physical addresses into `stripe_pages`.
- `stripe_uptodate_bitmap`: valid private sectors.
- `error_bitmap`: per-sector read/write/csum failures.
- `dbitmap`: horizontal stripe sectors affected by submitted bios.

Helpers such as `rbio_sector_index()`, `rbio_paddr_index()`, `sector_paddrs_in_rbio()`, and `index_rbio_pages()` provide the address mapping used by all RMW, recovery, and scrub paths.

## Write Path

`raid56_parity_write()` builds an rbio for the incoming bio, records affected horizontal sectors in `dbitmap`, and uses block plugging to merge partial stripes before scheduling work.

`rmw_rbio()` handles both full-stripe and sub-stripe writes:

1. Allocate parity pages.
2. For sub-stripe writes, allocate/read missing data pages unless all data sectors were cached.
3. For data block groups, lookup checksums and verify read data; mixed metadata/data groups skip checksum lookup to avoid deadlock.
4. Recover any missing/corrupt sectors within RAID tolerance.
5. Set `RBIO_RMW_LOCKED_BIT` to prevent further merging.
6. Cache sub-stripe data pages if safe.
7. Generate P and Q parity with xor or `raid6_call.gen_syndrome()`.
8. Assemble writes for changed data and parity sectors.
9. Duplicate the replace source stripe to the replace target when device replace is active.
10. Wait for all submitted write bios and fail if vertical error counts exceed tolerance.

## Read Recovery

`raid56_parity_recover()` is called after normal reads fail. It marks failed sectors in `error_bitmap`, optionally injects an extra RAID6 failure for alternate mirror retry attempts, and schedules recovery.

`recover_rbio()` reads all non-failed sectors, including parity, without trusting cached sectors. `recover_sectors()` reconstructs failed vertical stripes using RAID5 XOR, RAID6 data+P recovery, or RAID6 two-data recovery as appropriate. Reconstructed data sectors are checksum-verified when checksums are available.

## Parity Scrub

Scrub rbios are special zero-length-bio rbios used to verify or repair parity stripes. `raid56_parity_alloc_scrub_rbio()` identifies the parity stripe being scrubbed and copies the caller’s data bitmap.

`scrub_rbio()` allocates only essential pages, reads missing sectors, recovers recoverable data failures, then `finish_parity_scrub()` recalculates parity and writes only sectors whose scrubbed parity differs. During device replace, parity writes are duplicated to the replacement target when the scrubbed stripe is the replace source.

`raid56_parity_cache_data_folios()` lets scrub preload known-good file data and avoid unnecessary reads.

## Dependencies

This file depends on Btrfs volume mapping, checksums, workqueues, bio submission, extent/page helpers, device replace mapping, Linux RAID6 syndrome/recovery helpers, XOR helpers, tracepoints, and filesystem-sector/page-size alignment invariants.

## Concurrency And Error Handling

- Stripe ownership is protected by per-bucket spinlocks and each rbio’s `bio_list_lock`.
- Async work runs on `fs_info->rmw_workers`.
- Submitted bios are counted with `stripes_pending`; waiters sleep on `io_wait`.
- End I/O updates `error_bitmap` atomically per bit.
- Missing devices are treated as sector errors and checked against `bioc->max_errors`.
- Public entry points end the original bio with translated block status on allocation, read, write, recovery, or scrub failure.

## Risks And Invariants

- The stripe lock/hash logic must keep rbio references, hash membership, cache membership, and plug-list ownership balanced.
- `RBIO_RMW_LOCKED_BIT` is the boundary after which no more bios may merge into a write.
- Cached data is trusted only when `RBIO_CACHE_READY_BIT` and uptodate bits are set.
- Checksum lookup is intentionally skipped for metadata or mixed block groups to avoid recursive RAID56 recovery deadlocks.
- Device replace uses `replace_stripe_src` and the synthetic target stripe index; wrong stripe selection would miss replacement writes.
- RAID6 retry mirror numbering deliberately marks an additional stripe failed to try alternate reconstruction.

## Testing Signals

Relevant tests should cover full-stripe writes, sub-stripe RMW, cached RMW reuse, degraded writes, missing devices, RAID5 and RAID6 read recovery, RAID6 alternate mirror retries, checksum mismatch recovery, parity scrub repair, scrub with cached folios, device replace duplication, and block-size greater than page-size configurations.
