# File Research: sources/local-fs/kdave-linux/fs/btrfs/raid56.c

## Purpose

`raid56.c` implements Btrfs RAID5/RAID6 full-stripe handling: parity writes, read recovery, read-modify-write, stripe locking/merging, stripe cache reuse, scrub parity verification/repair, and device-replace duplication for RAID56 stripes.

The core unit is `struct btrfs_raid_bio` from `raid56.h`, which represents one full RAID56 stripe: data stripes plus P/Q parity stripes.

## Main Responsibilities

- Allocate and free RAID56 stripe state.
- Convert logical stripe sectors into page/physical-address arrays used for block IO.
- Merge partial writes into larger/full stripe writes when possible.
- Serialize access to a full stripe with a per-filesystem stripe hash table.
- Cache recently read/reconstructed data stripe pages to avoid repeated disk reads.
- Generate RAID5 P parity or RAID6 P/Q syndrome data.
- Recover failed data/parity sectors from remaining stripes.
- Verify data checksums during RMW reads when available.
- Scrub parity stripes and repair parity mismatches.
- Duplicate writes to a device-replace target when RAID56 replace is active.

## Key Data Structures

- `struct btrfs_stripe_hash`: one hash bucket, with `hash_list` and lock.
- `struct btrfs_stripe_hash_table`: owns the hash table plus an LRU `stripe_cache`.
- `struct btrfs_raid_bio`: full-stripe operation state, including bio list, stripe pages, physical-address arrays, error bitmap, uptodate bitmap, checksum buffers, work item, and stripe/cache lists.

Important internal flags:

- `RBIO_RMW_LOCKED_BIT`: no more bios may merge into this rbio.
- `RBIO_CACHE_BIT`: rbio is stored as a stripe cache entry.
- `RBIO_CACHE_READY_BIT`: stripe pages are valid for cache reuse.

## Stripe Hashing, Locking, and Cache

`btrfs_alloc_stripe_hash_table()` allocates the per-filesystem stripe hash table. The code hashes on `bioc->full_stripe_logical` via `rbio_bucket()`.

`lock_stripe_add()` is the central stripe serialization routine. It handles three cases:

- No existing rbio for the full stripe: insert this rbio as lock owner.
- Existing compatible rbio: merge bios with `merge_rbio()`.
- Existing incompatible/running rbio: append to the lock owner’s `plug_list`.

If a cached rbio exists and has no active IO, the new rbio can steal cached data pages with `steal_rbio()`.

`unlock_stripe()` releases ownership and either keeps the rbio in cache, removes it, or hands the stripe lock to the next waiting rbio. Depending on the waiting rbio operation, it schedules recovery, write RMW, or scrub work.

The cache is an LRU bounded by `RBIO_CACHE_SIZE`. `cache_rbio_pages()` copies bio-backed sectors into private stripe pages and marks sectors uptodate; `cache_rbio()` inserts/moves the rbio on the LRU. `remove_rbio_from_cache()` and `btrfs_clear_rbio_cache()` prune cached entries.

## Addressing and Page Indexing

The file supports sector sizes both smaller and larger than `PAGE_SIZE`. It uses:

- `sector_nsteps`: number of page-sized steps needed for one filesystem sector.
- `bio_paddrs[]`: physical addresses from upper-layer bios.
- `stripe_paddrs[]`: physical addresses from rbio-owned stripe pages.
- `stripe_pages[]`: allocated pages for full stripe data/parity.

Important helpers:

- `rbio_sector_index()`
- `rbio_paddr_index()`
- `rbio_stripe_paddr()`
- `rbio_stripe_paddrs()`
- `sector_paddrs_in_rbio()`
- `sector_paddr_in_rbio()`
- `index_rbio_pages()`
- `index_stripe_sectors()`

These helpers abstract whether a sector is sourced from the original bio list or rbio-private pages.

## Write Path

Public entry point: `raid56_parity_write()`.

Flow:

1. Allocate rbio with `alloc_rbio()`.
2. Add the incoming bio with `rbio_add_bio()`, updating `dbitmap`.
3. If the stripe is partial and there is a block plug, queue it for later batching.
4. Otherwise schedule `rmw_rbio_work()`.

Plug handling is done by `struct btrfs_plug_cb` and `raid_unplug()`, which sorts rbios by sector and merges compatible adjacent work before scheduling.

`rmw_rbio()` handles the actual write:

- Allocates parity pages first.
- If partial and missing data, allocates data pages and reads the stripe with `rmw_read_wait_recover()`.
- Locks the rbio against further merging.
- Caches partial-stripe data if suitable.
- Regenerates parity for every vertical sector with `generate_pq_vertical()`.
- Builds write bios with `rmw_assemble_write_bios()`.
- Submits writes and waits for completion.
- Checks if write errors exceeded RAID tolerance.

## Parity Generation

`generate_pq_vertical_step()` maps one sector step from each data stripe plus parity buffers. For RAID6 it calls `raid6_call.gen_syndrome()`. For RAID5 it copies the first data stripe into P and XORs the rest with `xor_gen()`.

`generate_pq_vertical()` repeats that per step and marks P/Q sectors uptodate.

## Read Recovery

Public entry point: `raid56_parity_recover()`.

It is called after normal read failure. It:

1. Allocates an rbio.
2. Adds the failed bio to the bio list.
3. Marks failed sectors in `error_bitmap` with `set_rbio_range_error()`.
4. For RAID6 mirror retries above mirror 2, marks an extra stripe failed with `set_rbio_raid6_extra_error()`.
5. Schedules `recover_rbio_work()`.

`recover_rbio()` reads all non-failed sectors, then `recover_sectors()` reconstructs failed vertical sectors. Recovery uses `recover_vertical()` and `recover_vertical_step()`.

Recovery supports:

- RAID5 single failure via P XOR reconstruction.
- RAID6 single failure via RAID5-style reconstruction when applicable.
- RAID6 two-data failure via `raid6_2data_recov()`.
- RAID6 data+P failure via `raid6_datap_recov()`.

`verify_one_sector()` optionally verifies reconstructed data against checksums.

## Checksum-Aware RMW

`fill_data_csums()` looks up data checksums for a full stripe before partial-stripe RMW reads. It avoids mixed data/metadata groups to prevent deadlocks while the full stripe lock is held.

`verify_bio_data_sectors()` checks read data sectors against the checksum buffer and marks mismatches in `error_bitmap`. This allows RMW to reconstruct corrupted data before parity is regenerated, reducing the risk of writing parity based on bad data.

If checksum lookup fails, the file warns that the sub-stripe write is not safe but continues without checksum protection.

## Scrub and Replace

Scrub entry points:

- `raid56_parity_alloc_scrub_rbio()`
- `raid56_parity_submit_scrub_rbio()`
- `raid56_parity_cache_data_folios()`

Scrub allocates an rbio for parity checking and tracks the parity stripe being scrubbed in `scrubp`.

`scrub_rbio()`:

1. Allocates only pages needed for sectors present in `dbitmap`.
2. Reads missing sectors.
3. Recovers failed sectors if possible with `recover_scrub_rbio()`.
4. Recomputes and verifies parity with `finish_parity_scrub()`.
5. Writes repaired parity sectors.

`finish_parity_scrub()` recomputes expected parity into temporary pages, compares against the scrubbed parity stripe, repairs mismatches in memory, then writes changed parity sectors. If device replace is active and the scrubbed parity stripe is the replace source, it also writes to the replace target.

`raid56_parity_cache_data_folios()` lets scrub preload known-good data folios into rbio-owned pages to avoid extra reads.

## Error Handling and Completion

Read and write bios are submitted through bio lists. Completion handlers update error/uptodate state and wake waiters through `stripes_pending` and `io_wait`.

- `raid_wait_read_end_io()` marks IO errors or sets pages uptodate and verifies checksums.
- `raid_wait_write_end_io()` records write errors.
- `rbio_orig_end_io()` ends upper-layer bios, frees checksum buffers, unlocks the stripe, and frees the rbio reference.

The code uses `error_bitmap` at sector granularity and checks failures per vertical stripe with `get_rbio_vertical_errors()` against `bioc->max_errors`.

## Notable Invariants

- A full stripe is fixed around `BTRFS_STRIPE_LEN`.
- `real_stripes` excludes replace target stripes.
- `nr_data = real_stripes - parity_stripes`.
- Cached rbios must have all data stripe pages present and uptodate.
- Parity pages are regenerated for writes rather than stolen from cache.
- `RBIO_RMW_LOCKED_BIT` prevents late merge after the write/recovery phase becomes immutable.
