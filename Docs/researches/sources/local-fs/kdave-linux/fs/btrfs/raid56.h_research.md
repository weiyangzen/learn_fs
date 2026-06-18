# File Research: sources/local-fs/kdave-linux/fs/btrfs/raid56.h

## Purpose

`raid56.h` declares Btrfs RAID5/RAID6 parity interfaces and defines the core `struct btrfs_raid_bio` state object used by `raid56.c`.

## Main Types

`enum btrfs_rbio_ops` identifies the operation type:

- `BTRFS_RBIO_WRITE`
- `BTRFS_RBIO_READ_REBUILD`
- `BTRFS_RBIO_PARITY_SCRUB`

`struct btrfs_raid_bio` represents one full RAID56 stripe, including data stripes and P/Q parity. The header documents how upper-layer bio pages and rbio-private stripe pages are represented.

Important fields:

- `bioc`: mapped IO context containing stripes/devices.
- `hash_list`: full-stripe lock hash membership.
- `stripe_cache`: LRU cache membership.
- `work`: workqueue item for async processing.
- `bio_list` and `bio_list_lock`: upper-layer bios and merge protection.
- `plug_list`: pending rbios for plugged writes and stripe lock handoff.
- `flags`: merge/cache/lock state bits.
- `operation`: current rbio operation.
- `nr_pages`, `nr_sectors`, `nr_data`, `real_stripes`: stripe geometry.
- `stripe_npages`, `stripe_nsectors`, `sector_nsteps`: page/sector layout.
- `scrubp`: parity stripe being scrubbed.
- `dbitmap`: horizontal sectors that contain data for the current operation.
- `stripe_pages`: rbio-owned pages.
- `bio_paddrs`: physical addresses from upper-layer bios.
- `stripe_paddrs`: physical addresses from `stripe_pages`.
- `stripe_uptodate_bitmap`: sectors in private stripe storage known valid.
- `error_bitmap`: sectors with IO/checksum errors.
- `csum_buf`, `csum_bitmap`: optional checksum verification state.

The header’s long comment is important because it defines the addressing model: sectors are located by `stripe_nr`, `sector_nr`, `step_nr`, and source array (`bio_paddrs` versus `stripe_paddrs`). `step_nr` exists for block-size-greater-than-page-size support.

`struct raid56_bio_trace_info` carries trace metadata for submitted device bios: device id, offset inside stripe, and stripe number.

## Helper Macros and Inline Functions

- `nr_data_stripes()` returns data stripe count from a chunk map.
- `nr_bioc_data_stripes()` returns data stripe count from an IO context.
- `RAID5_P_STRIPE` and `RAID6_Q_STRIPE` encode parity stripe sentinels.
- `is_parity_stripe()` checks those sentinel values.

## Public Interfaces

- `raid56_parity_recover()`: recover a failed read bio.
- `raid56_parity_write()`: submit a RAID56 parity write.
- `raid56_parity_alloc_scrub_rbio()`: allocate scrub rbio.
- `raid56_parity_submit_scrub_rbio()`: submit scrub rbio.
- `raid56_parity_cache_data_folios()`: preload scrub data.
- `btrfs_alloc_stripe_hash_table()`: initialize stripe locking/cache table.
- `btrfs_free_stripe_hash_table()`: free stripe locking/cache table.

## Relationships

This header is consumed by the RAID56 implementation and by Btrfs scrub, volume mapping, and IO paths that need to submit RAID56 writes, recovery, or parity scrub operations.
