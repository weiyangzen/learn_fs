# File Research: sources/local-fs/btrfs-progs/check/common.h

## Scope

This header defines shared in-memory records and cache/tree containers used by Btrfs check code for chunk, block-group, and device-extent validation.

## Public APIs And Data Structures

- Declares global `gfs_info`.
- `struct block_group_record` tracks an on-disk block group item plus actual/disk usage and list/cache links.
- `struct block_group_tree` wraps the block-group cache tree, pending extents tree, and block-group list.
- `struct stripe` records one chunk stripe’s devid, offset, and device UUID.
- `struct chunk_record` records a chunk item, stripes, type/profile fields, block-group linkage, device-extents list, and alignment status.
- `struct device_extent_record` records a device extent and its links into chunk/device orphan lists.
- `struct device_extent_tree` stores device extents plus orphan lists for extents missing chunk or device ownership.
- Inline helpers initialize block-group and device-extent trees, compute flexible `chunk_record` size, and validate `num_stripes`.
- Declares insertion/free helpers, record constructors from tree leaves, `calc_stripe_length()`, and `check_chunks()`.

## Dependencies

- Uses Btrfs core types from `kernel-shared/ctree.h`.
- Uses `cache_tree`/`cache_extent`, `extent_io_tree`, and kernel-style lists.
- Consumed by chunk/device/block-group check and repair paths.

## Risks And Invariants

- `check_num_stripes()` prevents divide-by-zero and invalid RAID5/RAID6 stripe counts.
- Chunk and device-extent orphan lists are part of correctness reporting; moving records between lists must preserve ownership semantics.
- `chunk_record` uses a flexible trailing stripe array, so allocations must use `btrfs_chunk_record_size()`.
