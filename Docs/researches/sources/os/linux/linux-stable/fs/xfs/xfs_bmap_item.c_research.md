# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_bmap_item.c

## Purpose

Implements bmap update intent/done log items: BUI and BUD. These make deferred bmbt map/unmap updates replayable after crashes.

## Main Responsibilities

- Allocates, formats, releases, and recovers BUI intent items.
- Allocates and formats BUD done items.
- Logs deferred bmap update records into BUI items.
- Sorts bmap intents by inode when requested.
- Queues deferred bmap update work.
- Finishes one bmap update through `xfs_bmap_finish_one`.
- Reconstructs and replays bmap work during log recovery.
- Relogs BUI items to move the log tail.

## Logged Record Contents

Each `xfs_map_extent` records:
- owner inode
- start block
- file offset
- length
- map vs unmap operation
- unwritten state
- attr fork flag
- realtime flag

`XFS_BUI_MAX_FAST_EXTENTS` is currently one, so each BUI contains one mapping operation.

## Important Invariants

- BUI refcounting accounts for log ownership and BUD ownership.
- Mapping records must pass inode, file extent, and physical extent validation before recovery.
- Realtime flag must match the recovered inode fork’s realtime status.
- Map intents temporarily add to `i_delayed_blks` so stat/block accounting remains sensible during out-of-place overwrite operations.
- Deferred group intent references keep AG/rtgroup state live across transaction rolls.

## Recovery Flow

Recovery validates the BUI, obtains the target inode, reconstructs an `xfs_bmap_intent`, allocates an itruncate-style transaction reservation, joins the inode, checks extent count expansion, finishes the intent, and commits captured deferred operations.

## Dependencies

- XFS deferred operation framework.
- Bmbt update code.
- Log recovery and AIL item matching.
- AG/rtgroup intent reference tracking.
- Inode extent-count reservation helpers.

## Research Notes

This file is the redo logging layer for bmbt updates. It is closely coupled to rmap/refcount deferred work because completing a bmap update can queue additional metadata intents.
