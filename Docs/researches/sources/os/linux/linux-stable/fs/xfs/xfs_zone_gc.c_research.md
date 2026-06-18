# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_zone_gc.c

## Purpose

Implements garbage collection for zoned XFS. GC evacuates live extents from partially used zones into GC target zones, remaps files to the new locations, and resets empty zones for reuse.

## Main Responsibilities

- Determines when GC is needed from available/free realtime counters and low-space policy.
- Allocates GC state, scratch folios, bioset, and rmap lookahead records.
- Selects victim zones from reclaimable used-block buckets.
- Queries victim-zone rmap records and sorts them by inode/offset.
- Reads live file extents into scratch buffers.
- Allocates GC target blocks from reserved pools.
- Writes chunks using zone append or conventional writes, splitting at hardware append limits.
- Finishes chunks by breaking layouts, waiting for DIO, and calling `xfs_zoned_end_io`.
- Resets empty zones after flushing the realtime device and forcing rmap inode logs.
- Runs the `xfs-zone-gc` kthread with park/unpark, freezer, stop, and wakeup support.

## Important Invariants

- GC zones use reserved capacity to avoid deadlock with user writers waiting for GC.
- Victim zones with active GC references are skipped.
- GC I/O completions are processed in order to preserve sorted remap behavior.
- Reflink is not supported on zoned filesystems because GC would break sharing.
- Zone reset is issued only after used blocks reach zero and relevant metadata is forced.
- Failed GC I/O forces metadata I/O shutdown.

## Dependencies

Uses XFS rtrmap btrees, inode cache, realtime group references, zoned allocator APIs, bio/bioset APIs, block queue limits, free counters, log forcing, and kthread/freezer infrastructure.

## Research Notes

This is a speculative copy-and-remap collector. The central safety property is that `xfs_zoned_end_io` verifies mappings have not changed before remapping newly copied data.
