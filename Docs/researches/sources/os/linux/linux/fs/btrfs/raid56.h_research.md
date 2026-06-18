# File Research: sources/os/linux/linux/fs/btrfs/raid56.h

## Scope

`raid56.h` declares the RAID56 rbio model, operation types, trace metadata, helper constants, and public interfaces implemented by `raid56.c`.

## Key Types And Constants

- `enum btrfs_rbio_ops`: write, read rebuild, and parity scrub operations.
- `struct btrfs_raid_bio`: full-stripe state for RAID5/6 data and parity I/O.
- `struct raid56_bio_trace_info`: devid, stripe offset, and stripe number for trace events.
- `RAID5_P_STRIPE` and `RAID6_Q_STRIPE`: sentinel parity stripe identifiers.
- `is_parity_stripe()`: tests those parity sentinels.

## Rbio Data Model

The header documents two page sources:

- Higher-layer bios stored in `bio_list`, indexed by `bio_paddrs`.
- Internal rbio pages stored in `stripe_pages`, indexed by `stripe_paddrs`.

Addressing is by stripe number, sector number, and step number. Step addressing exists for block-size greater than page-size support, where one filesystem sector spans multiple pages.

`struct btrfs_raid_bio` also stores hash/cache lists, plug list, operation flags, stripe geometry, refcount, pending I/O counter, waitqueue, data/parity bitmaps, checksum buffers, and error tracking.

## Public APIs

- `raid56_parity_write()`
- `raid56_parity_recover()`
- `raid56_parity_alloc_scrub_rbio()`
- `raid56_parity_submit_scrub_rbio()`
- `raid56_parity_cache_data_folios()`
- `btrfs_alloc_stripe_hash_table()`
- `btrfs_free_stripe_hash_table()`

Inline helpers compute data stripe counts from chunk maps and bio contexts.

## Dependencies

The header depends on Linux list, spinlock, bio, refcount, workqueue APIs, and Btrfs volume mapping definitions.

## Risks And Invariants

The structure layout encodes key assumptions used by `raid56.c`: fixed 64K stripe length, parity stripes placed after data stripes, all rbio sector arrays covering the full stripe, and `error_bitmap`/`stripe_uptodate_bitmap` sized per full-stripe sector.
