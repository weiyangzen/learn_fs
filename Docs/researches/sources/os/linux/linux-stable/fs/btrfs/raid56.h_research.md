# File Research: sources/os/linux/linux-stable/fs/btrfs/raid56.h

## Purpose

Declares Btrfs RAID56 parity interfaces and defines the central `struct btrfs_raid_bio` used by `raid56.c`.

## Main Types

`enum btrfs_rbio_ops` identifies rbio operation mode:

- `BTRFS_RBIO_WRITE`
- `BTRFS_RBIO_READ_REBUILD`
- `BTRFS_RBIO_PARITY_SCRUB`

`struct btrfs_raid_bio` represents one full RAID56 stripe, including all data stripes and parity stripes. It stores:

- The `btrfs_io_context`.
- Hash/cache/plug list nodes.
- Work item for async processing.
- Upper-layer bio list and lock.
- Operation flags.
- Stripe geometry: pages, sectors, data stripes, real stripes, sector steps.
- Pending I/O accounting and waitqueue.
- Data bitmap and scrub/finish bitmap.
- Page/address arrays for upper bios and internal stripe pages.
- Uptodate and error bitmaps.
- Optional checksum buffer and checksum bitmap.

The header contains an extensive design comment explaining the mapping between upper-layer bios, internal pages, sector addressing, stripe numbers, and step numbers.

`struct raid56_bio_trace_info` records trace metadata for each physical bio: device id, stripe-relative offset, and stripe number.

## Helpers

Inline helpers:

- `nr_data_stripes()` computes chunk-map data stripe count.
- `nr_bioc_data_stripes()` computes io-context data stripe count.

Constants:

- `RAID5_P_STRIPE`
- `RAID6_Q_STRIPE`
- `is_parity_stripe()`

## Exported API

Declared functions:

- `raid56_parity_recover()`
- `raid56_parity_write()`
- `raid56_parity_alloc_scrub_rbio()`
- `raid56_parity_submit_scrub_rbio()`
- `raid56_parity_cache_data_folios()`
- `btrfs_alloc_stripe_hash_table()`
- `btrfs_free_stripe_hash_table()`

## Role in the Subsystem

This header is the RAID56 contract between the Btrfs volume/I/O layer and parity implementation. It exposes only high-level submission and lifecycle functions while keeping the RMW, recovery, and scrub algorithms private to `raid56.c`.
