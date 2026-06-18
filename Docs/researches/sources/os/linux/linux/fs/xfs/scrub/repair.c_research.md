# File Research: sources/os/linux/linux/fs/xfs/scrub/repair.c

## Purpose
Provides shared online repair infrastructure for XFS scrub. It coordinates repair attempts, transaction rolling, reservation estimation, per-AG and realtime cursor setup, btree root discovery, quota handling, metadata inode repair, temporary in-memory btree setup, and reservation reset helpers.

## Major Components
- Repair orchestration:
  - `xrep_attempt`
  - `xrep_will_attempt`
  - `xrep_failure`
  - `xrep_probe`
- Transaction helpers:
  - `xrep_roll_ag_trans`
  - `xrep_roll_trans`
  - `xrep_defer_finish`
- Reservation helpers:
  - `xrep_ag_has_space`
  - `xrep_calc_ag_resblks`
  - `xrep_calc_rtgroup_resblks`
  - `xrep_reset_perag_resv`
  - `xrep_reset_metafile_resv`
- AG and rtgroup setup:
  - `xrep_ag_btcur_init`
  - `xrep_ag_init`
  - `xrep_rtgroup_btcur_init`
  - `xrep_rtgroup_init`
- Root discovery:
  - `xrep_find_ag_btree_roots`
  - `xrep_findroot_rmap`
  - `xrep_findroot_block`
- Metadata inode repair:
  - `xrep_metadata_inode_subtype`
  - `xrep_metadata_inode_forks`
  - `xrep_ino_ensure_extent_count`
  - `xrep_inode_set_nblocks`
- Quota helpers under `CONFIG_XFS_QUOTA`.

## Control Flow and Invariants
`xrep_attempt` clears scrub btree cursors, invokes the scrub operation’s repair callback, updates stats, and returns `-EAGAIN` when scrub should rerun. It handles:
- success by clearing output flags and setting `XREP_ALREADY_FIXED`;
- `-ECHRNG` by requesting intent drain;
- `-EDEADLOCK` by retrying with `XCHK_TRY_HARDER`.

Transaction rolling preserves AG header buffer locks by logging, holding, rolling, and rejoining AGI/AGF buffers. Deferred work uses similar hold/release logic around `xfs_defer_finish`.

Reservation estimation computes worst-case rebuild space for per-AG btrees from AGI/AGF counters, with fallback assumptions when headers are corrupt. Realtime group reservation estimates currently calculate rtrmapbt size from rtgroup extents.

Metadata inode repair runs subordinate scrub/repair passes for inode core and forks, clears illegal reflink state, and removes attr forks on non-metadir metadata files.

## Dependencies and Integration
This is the shared repair layer used by nearly every specialized repair file in this group:
- Refcount/rmap repairs rely on transaction rolling, btree root/cursor helpers, and reservation reset.
- Realtime repairs use rtgroup setup and `xrep_require_rtext_inuse`.
- Metadata-inode btree repairs use `xrep_setup_xfbtree`, `xrep_metadata_inode_forks`, `xrep_inode_set_nblocks`, and buffer verification helpers.

## Risk and Edge Cases
- Repair transaction code deliberately holds clean AG header buffers across rolls to preserve AG locks.
- Root discovery is best-effort and depends on healthy rmap data and recognizable buffer verifiers.
- Quota repair cannot allocate dquot blocks in transaction context; quota corruption forces a later quotacheck.
- Realtime reservation sizing only accounts for rtrmapbt in this file, despite nearby rtrefcount repair users.
