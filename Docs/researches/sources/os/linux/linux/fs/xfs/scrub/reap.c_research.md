# File Research: sources/os/linux/linux/fs/xfs/scrub/reap.c

## Role
Disposes of old metadata blocks after online repair constructs replacement metadata. It handles AG metadata, file metadata, metadir metadata, CoW staging extents, realtime CoW extents, and complete inode forks.

## Core State
- `struct xreap_state` carries scrub context, owner information or inode/fork, buffer invalidation counts, and deferred-intent limits.
- Limit helpers throttle buffer invalidation and deferred work so transactions do not exceed log reservations.

## Buffer Scanning
- `xrep_bufscan_max_sectors` and `xrep_bufscan_advance` search for incore buffers of plausible sizes.
- Reap invalidates buffers before freeing blocks when it believes no other owner remains.
- Oversized/non-loggable file buffers are staled directly instead of logged.

## AG/FS Metadata Reap
- `xreap_agextent_select` uses rmapbt to split extents into crosslinked and non-crosslinked runs.
- `xreap_agextent_iter` removes rmaps for crosslinked blocks or frees single-owner blocks.
- CoW extents use refcount cleanup; AGFL blocks are returned one at a time.
- `xrep_reap_agblocks` and `xrep_reap_fsblocks` walk bitmaps and finish deferred work.

## Realtime Reap
- Under `CONFIG_XFS_RT`, realtime CoW extents are split by realtime rmap crosslink state.
- `xrep_reap_rtblocks` locks realtime group bitmap/rmap/refcount state and frees or unmaps CoW extents.

## Metadir Reap
- `xrep_reap_metadir_fsblocks` reaps old metadir btree blocks with regular AG reservation semantics and then resets metafile reservation accounting.

## Inode Fork Reap
- `xrep_reap_ifork` walks every real mapping in an inode fork and removes it.
- `xreap_bmapi_select` determines crosslink status using rmap owner including file offset.
- Crosslinked mappings are unmapped from the fork and rmap only; non-crosslinked mappings also invalidate buffers and free space.
- Quota block counts are adjusted during fork unmap.

## Risk Points
- Reap intentionally cannot fix all possible buffer-cache aliasing crosslinks.
- Crash during very large reap chains can leak blocks, so deferral chains are periodically finished.
- Requires rmapbt for ownership/crosslink decisions.
