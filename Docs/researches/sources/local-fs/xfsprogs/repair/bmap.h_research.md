# File Research: sources/local-fs/xfsprogs/repair/bmap.h

## Purpose

`bmap.h` declares the repair-local block map used to map inode fork logical block offsets to filesystem blocks.

## Main Types

- `bmap_ext_t` describes one mapping extent with logical start, physical start, and length.
- `blkmap_t` is a dynamically sized array of extents with capacity and active-count fields.

## Public API

The header exposes allocation, freeing, insertion, single-block lookup, multi-block lookup, last-offset query, and next-offset iteration functions. It also declares the data and attribute fork thread-local keys.

## Important Invariants

- `BLKMAP_SIZE(n)` computes the allocation size for `n` extent records.
- `blkmap_alloc` requires a data or attr fork selector.
- The map is an in-memory repair helper and does not own on-disk metadata.

## Research Notes

This header is small but central to attribute and directory repair because DA blocks are read by first translating file block numbers through this map.
