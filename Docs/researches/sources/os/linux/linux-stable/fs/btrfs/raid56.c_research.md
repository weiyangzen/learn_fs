# File Research: sources/os/linux/linux-stable/fs/btrfs/raid56.c

## Purpose

Implements Btrfs RAID5/RAID6 parity I/O for writes, failed-read reconstruction, parity scrub, and device-replace duplication. The central object is `struct btrfs_raid_bio` (`rbio`), representing one full RAID56 stripe: all data stripes plus P and optional Q parity stripes.

The file handles:

- Partial-stripe read-modify-write (RMW).
- Full-stripe write fast paths.
- Stripe locking and rbio merging.
- Stripe cache reuse for recently read data stripes.
- RAID5 XOR parity and RAID6 P/Q syndrome generation.
- Recovery from missing devices, read errors, and checksum mismatches.
- Parity scrub validation and repair.
- Replace target writes for affected stripes.

## Core Concepts

`rbio` tracks one full stripe. The code distinguishes:

- `bio_paddrs`: physical addresses borrowed from upper-layer bios.
- `stripe_pages` / `stripe_paddrs`: pages allocated internally for reads, parity, recovery, scrub, and cache.
- `error_bitmap`: per-sector failures across all stripes.
- `stripe_uptodate_bitmap`: per-sector validity of `stripe_paddrs`.
- `dbitmap`: horizontal-sector bitmap showing which vertical stripes are touched by the upper-layer write or scrub.

The implementation supports sector sizes both smaller and larger than page size through `sector_nsteps`, where a filesystem block may map to one or more page-sized steps.

## Stripe Locking and Cache

The file defines a global per-filesystem stripe hash table via `btrfs_alloc_stripe_hash_table()` and frees it with `btrfs_free_stripe_hash_table()`.

Important behavior:

- `lock_stripe_add()` serializes work for the same full stripe.
- Compatible rbios can be merged before final RMW locking.
- Incompatible rbios are queued on `plug_list` and started when the current rbio unlocks.
- Cached rbios can donate uptodate data pages to later rbios with `steal_rbio()`.
- `unlock_stripe()` either keeps an rbio in cache, hands the lock to the next queued rbio, or removes it from the hash/cache.

Cache entries are LRU-limited by `RBIO_CACHE_SIZE`. Cached data is considered reusable only after `RBIO_CACHE_READY_BIT` is set.

## Rbio Allocation and Address Indexing

`alloc_rbio()` allocates the rbio and its pointer arrays/bitmaps from the `btrfs_io_context`. It computes:

- `real_stripes`, excluding replace target stripes.
- `nr_data`, derived from RAID parity count.
- `stripe_npages`, `stripe_nsectors`, and `sector_nsteps`.
- `nr_pages` and `nr_sectors` for the full stripe.

Address helpers include:

- `rbio_sector_index()`
- `rbio_paddr_index()`
- `rbio_stripe_paddr()`
- `rbio_pstripe_paddr()`
- `rbio_qstripe_paddr()`
- `sector_paddrs_in_rbio()`
- `sector_paddr_in_rbio()`

These centralize stripe/sector/step translation and preserve support for block size greater than page size.

## Write Path

Entry point: `raid56_parity_write()`.

Flow:

1. Allocate an rbio.
2. Add the caller bio with `rbio_add_bio()`.
3. If partial and block-layer plugging is active, queue it for `raid_unplug()`.
4. Otherwise queue `rmw_rbio_work()`.

`raid_unplug()` sorts rbios by logical sector and merges adjacent compatible rbios where possible, improving the chance of full-stripe writes.

`rmw_rbio()` performs the actual write:

- Allocates parity pages first.
- If the rbio is partial and cache is insufficient, reads all needed data/parity sectors with `rmw_read_wait_recover()`.
- Uses checksums for data verification where available.
- Sets `RBIO_RMW_LOCKED_BIT` to prevent further merging.
- Caches partial-stripe data pages after read/repair.
- Regenerates parity for every sector with `generate_pq_vertical()`.
- Assembles write bios with `rmw_assemble_write_bios()`.
- Submits writes and waits for completion.
- Reports `-EIO` if post-write error count exceeds RAID tolerance.

Full-stripe writes avoid reading old data because every data sector is supplied by upper layers.

## Read Recovery Path

Entry point: `raid56_parity_recover()`.

Used after a normal read fails. It:

1. Allocates an rbio.
2. Adds the failed bio.
3. Marks the failed range in `error_bitmap` with `set_rbio_range_error()`.
4. For RAID6 retry mirrors greater than 2, marks an additional synthetic failed stripe with `set_rbio_raid6_extra_error()`.
5. Queues `recover_rbio_work()`.

`recover_rbio()` reads all nonfailed sectors, then calls `recover_sectors()`.

Recovery is per vertical stripe:

- `get_rbio_vertical_errors()` finds failed stripe indexes.
- `recover_vertical()` rejects errors beyond `bioc->max_errors`.
- `recover_vertical_step()` performs RAID5 XOR or RAID6 recovery:
  - single RAID5/RAID6 failures can use P parity.
  - RAID6 two-data or data-plus-P failures use RAID6 library helpers.
  - P/Q-only corruption can be skipped for data-read recovery.
- `verify_one_sector()` validates recovered data against checksums if available.

## Checksum Handling

`fill_data_csums()` loads data checksums for data block groups during RMW. It intentionally skips metadata and mixed block groups to avoid deadlock while holding the stripe lock.

Read completion calls `verify_bio_data_sectors()` for data stripes. Checksum mismatches mark bits in `error_bitmap`, allowing reconstruction to repair stale or corrupt data before parity generation.

If checksum lookup fails, the code warns and continues without checksum protection for that sub-stripe write.

## Parity Generation

`generate_pq_vertical_step()` maps one step from every data stripe and parity stripe.

- RAID5 copies the first data block into P and XORs the remaining data blocks.
- RAID6 invokes `raid6_call.gen_syndrome()` over all real stripes.

`generate_pq_vertical()` repeats this for all steps in one filesystem sector and marks parity sectors uptodate.

## Scrub and Replace

Scrub allocation entry: `raid56_parity_alloc_scrub_rbio()`.

Submit entry: `raid56_parity_submit_scrub_rbio()`.

Scrub flow:

1. `alloc_rbio_essential_pages()` allocates pages only for sectors needed by `dbitmap`.
2. `scrub_assemble_read_bios()` reads missing sectors unless already supplied or cached.
3. `recover_scrub_rbio()` repairs failed data sectors where RAID tolerance and scrub constraints allow.
4. `finish_parity_scrub()` verifies recalculated parity against the scrubbed parity stripe.
5. If mismatched, parity is repaired and written.
6. If device replace targets the scrubbed parity stripe, writes are duplicated to the replacement stripe.

`raid56_parity_cache_data_folios()` lets scrub provide known-good data folios, avoiding redundant reads by copying them into rbio-managed pages and marking sectors uptodate.

## Error and Completion Model

Read bios use `raid_wait_read_end_io()`:

- Bio I/O errors update `error_bitmap`.
- Successful reads mark internal pages uptodate and may perform checksum verification.

Write bios use `raid_wait_write_end_io()`:

- Bio I/O errors update `error_bitmap`.

All submitted bios decrement `stripes_pending` and wake `io_wait`. Original upper-layer bios are completed by `rbio_orig_end_io()` after unlock/cache handling.

## Concurrency

Major concurrency mechanisms:

- Stripe hash bucket spinlocks serialize stripe ownership.
- `bio_list_lock` protects rbio bio lists, plug lists, and merge state.
- `RBIO_RMW_LOCKED_BIT` prevents late merges once final RMW begins.
- Work is queued to `fs_info->rmw_workers`.
- Plug callbacks gather partial writes within block-layer plugging windows.
- Wait queues synchronize submitted stripe bios.

## Important Invariants

The file uses `ASSERT_RBIO*` helpers to dump `bioc` and `rbio` context before asserting. Key invariants include:

- Real stripes are between 2 and 255.
- Data stripes are less than total stripes.
- Stripe sectors fit in a machine word because current stripe length is fixed at 64 KiB.
- Physical address entries must not be `INVALID_PADDR` when mapped.
- Cached rbios must have all data stripe pages present and uptodate.

## External Interface

Exported functions:

- `btrfs_alloc_stripe_hash_table()`
- `btrfs_free_stripe_hash_table()`
- `raid56_parity_write()`
- `raid56_parity_recover()`
- `raid56_parity_alloc_scrub_rbio()`
- `raid56_parity_submit_scrub_rbio()`
- `raid56_parity_cache_data_folios()`

These are consumed by Btrfs volume mapping, writeback/read recovery, scrub, and device replace code.
