# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_aops.c

## Purpose

Implements XFS address-space operations for buffered I/O, DAX writeback, iomap read/writeback integration, write completion, and swap activation.

## Main Responsibilities

- Updates on-disk file size after append writeback through `xfs_setfilesize`.
- Completes write I/O:
  - COW extent conversion
  - unwritten extent conversion
  - zoned realtime completion
  - append size update
  - I/O error cleanup
- Queues I/O completion work through `xfs_end_bio` and `xfs_end_io`.
- Maps dirty folios for writeback through iomap callbacks.
- Handles normal writeback and zoned realtime writeback through separate writepage contexts.
- Provides read folio and readahead operations.
- Implements `bmap` support with restrictions for reflink and realtime files.
- Implements swap activation with inodegc flushing and correct block-device selection.

## Normal Writeback Flow

`xfs_map_blocks` validates or refreshes cached iomap mappings, checks the COW fork before the data fork, converts delalloc extents to real blocks, and trims mappings at COW boundaries. Failed mapping or I/O can punch stale delalloc ranges from clean folios.

`xfs_writeback_submit` can pre-convert COW extents and redirects ioends needing transactions to the XFS completion workqueue.

## Zoned Realtime Flow

Zoned writeback is separate:
- dirty data must be covered by COW-fork delalloc extents
- mapping removes delayed allocation records before submission
- physical allocation is deferred to `xfs_zone_alloc_and_submit`
- zone append completion records the written sector and releases open-zone references

## Important Invariants

- Completion work runs in `memalloc_nofs` context because writeback can originate from reclaim.
- Reflink COW and unwritten extent conversion require transactions and cannot be completed directly in interrupt context.
- Swap cannot use zoned realtime files, reflink/COW mappings via `bmap`, or unflushed shared extent removal state.
- Read I/O can use special iomap read ops when the block device has integrity checksums.

## Dependencies

- iomap writeback/read helpers.
- XFS bmap, reflink, iomap, inodegc, realtime group, and zoned allocation code.
- Bio integrity helpers for zoned writes with integrity metadata.

## Research Notes

This file is the central bridge between the Linux page cache/iomap layer and XFS metadata updates required by writeback completion.
