# File Research: sources/local-fs/xfsprogs/repair/bulkload.h

## Purpose

`bulkload.h` declares shared repair infrastructure for staging and bulk-loading rebuilt btrees.

## Main Types

- `struct repair_ctx` groups mount, inode, and transaction pointers.
- `struct bulkload_resv` describes one reserved extent of btree blocks.
- `struct bulkload` tracks reservation state, fake btree roots, owner information, allocation hints, and reserved block counts.

## Public API

The header exposes initialization for AG and inode btrees, block claiming, reservation addition/allocation, cancel/commit cleanup, and slack estimation helpers.

## Constants and Globals

- `bload_leaf_slack` and `bload_node_slack` are global tuning knobs.
- `XREP_MAX_ITRUNCATE_EFIS` caps deferred free extents per transaction roll.

## Important Invariants

- Callers must commit or cancel every initialized bulkload context.
- `for_each_bulkload_reservation` safely iterates reservations while deleting.
- Owner information must match the btree being rebuilt so rmap records are correct.

## Research Notes

This header abstracts the repetitive mechanics of reserving replacement btree blocks, making rebuild code focus on collecting records and configuring libxfs bulk-load callbacks.
