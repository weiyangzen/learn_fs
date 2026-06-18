# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/refcount_repair.c

## Purpose
Rebuilds a corrupt per-AG refcount btree from reverse mapping records. It reconstructs shared and CoW staging refcount records, bulk-loads a new refcountbt, commits it into the AGF, and reaps old refcountbt blocks.

## Major Components
- `struct xrep_refc`: repair state, including staged refcount records, new-btree state, old-tree bitmap, cursor position, and block counters.
- `xrep_setup_ag_refcountbt`: allocates xfbtree backing storage for the rmap record bag.
- `xrep_refc_find_refcounts`: sweep-line algorithm over rmap records using `rcbag`.
- `xrep_refc_stash` / `xrep_refc_stash_cow`: validate and store generated refcount records.
- `xrep_refc_build_new_tree`: stages, reserves, bulk-loads, and commits the new refcountbt.
- `xrep_refc_remove_old_tree`: reaps old refcountbt blocks.
- `xrep_refcountbt`: top-level repair entry point.

## Control Flow and Invariants
Repair requires rmapbt support. It scans the AG rmapbt and:
- Records CoW staging extents as CoW-domain refcount records with count 1.
- Records old refcountbt blocks in a bitmap for later reaping.
- Ignores non-shareable mappings when computing shared data extents.
- Uses a bag of active rmap intervals to emit a refcount record whenever overlap count changes and the previous count exceeds 1.

Generated records are sorted in ondisk refcountbt order, including shared records before CoW records. The sorter rejects overlap and domain ordering violations.

The new tree is built with `xrep_newbt_init_ag`, staged with an fake AG root, bulk-loaded, committed to the AGF, and followed by AGF counter reinitialization and transaction roll.

## Dependencies and Integration
Uses:
- `rcbag` for sweep-line overlap accounting.
- `xfarray` for generated refcount records.
- `xagb_bitmap` for old-tree block tracking.
- `xrep_newbt` for staging a new btree.
- `xrep_reap_agblocks` for safe old-block disposal.
- `xrep_reinit_pagf` and `xrep_roll_ag_trans` from `repair.c`.

## Risk and Edge Cases
- The repair cannot run without rmapbt because rmaps are the source of truth.
- Records are clamped to `XFS_REFC_REFCOUNT_MAX` if overlap exceeds representable refcount.
- It checks generated extents are not free space and not inode chunks before storing them.
- Alternate in-core refcountbt height is used during replacement to prevent verifier failures while old blocks may still be checkpointed.
