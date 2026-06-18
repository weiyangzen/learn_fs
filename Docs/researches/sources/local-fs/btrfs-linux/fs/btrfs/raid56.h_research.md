# File Research: sources/local-fs/btrfs-linux/fs/btrfs/raid56.h

This header defines the public RAID56 interface and the full in-memory rbio model used by `raid56.c`. It is included by RAID56 callers such as `bio.c`, `scrub.c`, `disk-io.c`, `volumes.c`, `block-group.c`, `extent-tree.c`, and `super.c`.

Public operation type:
- `enum btrfs_rbio_ops` distinguishes normal parity writes (`BTRFS_RBIO_WRITE`), read-time reconstruction (`BTRFS_RBIO_READ_REBUILD`), and parity scrub/repair (`BTRFS_RBIO_PARITY_SCRUB`).

`struct btrfs_raid_bio`:
- Represents one complete RAID5/RAID6 full stripe, including data and P/Q stripes.
- Owns a `btrfs_io_context` reference, hash/cache/plug/work list nodes, the original bio list, and the operation mode.
- Stores full-stripe geometry: number of pages, total sectors, data stripes, real stripes excluding replace targets, pages per stripe, sectors per stripe, and sector steps for block-size/page-size mismatches.
- Tracks original caller bio pages in `bio_paddrs` and internally allocated data/parity/recovery pages in `stripe_pages` plus `stripe_paddrs`.
- Uses `bio_list_bytes` and `dbitmap` to decide whether a write is a full-stripe write or a partial RMW.
- Uses `stripe_uptodate_bitmap` and `error_bitmap` for read/recovery/scrub state.
- Carries `finish_pointers` and `finish_pbitmap` as temporary parity-generation/scrub state.
- Optionally stores `csum_buf` and `csum_bitmap` for data-sector checksum verification during RMW/recovery.

Trace support:
- `struct raid56_bio_trace_info` records device id, offset inside the stripe, and stripe number for RAID56 read/write tracepoints.

Geometry helpers and constants:
- `nr_data_stripes()` computes data stripes for a chunk map by subtracting parity stripes from `map->num_stripes`.
- `nr_bioc_data_stripes()` performs the same calculation for an active `btrfs_io_context`.
- `RAID5_P_STRIPE`, `RAID6_Q_STRIPE`, and `is_parity_stripe()` provide sentinel values used outside this file to identify parity stripes.

Exported functions:
- `raid56_parity_write()` submits a normal RAID56 write.
- `raid56_parity_recover()` reconstructs failed read bios.
- `raid56_parity_alloc_scrub_rbio()`, `raid56_parity_submit_scrub_rbio()`, and `raid56_parity_cache_data_folios()` support scrub and device replace parity repair.
- `btrfs_alloc_stripe_hash_table()` and `btrfs_free_stripe_hash_table()` manage the per-filesystem stripe lock/cache table.

Important invariants:
- The header documents the addressing model used throughout `raid56.c`: stripe number, sector number, step number, and whether the sector comes from higher-layer bios or internal pages.
- `INVALID_PADDR` is private to `raid56.c`, but the header’s comments establish that invalid physical-address entries mean no page is available for a given sector/step.
- The structure is tightly coupled to the fixed `BTRFS_STRIPE_LEN` full-stripe model and to page/sector alignment rules enforced in `alloc_rbio()`.
