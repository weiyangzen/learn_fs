# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/reap.c

This file disposes of old metadata blocks after online repair has built replacement structures.

Core problem:
- Rebuilt metadata leaves old blocks that may be singly owned, crosslinked, stale, or missing reverse mappings.
- Reaping uses rmap/refcount information to decide whether to free blocks or only remove this owner’s reverse mapping.
- It also invalidates buffer-cache entries for blocks being freed where possible.

State:
- `struct xreap_state` tracks scrub context, owner info or inode/fork, buffer invalidation count, deferred operation count, and transaction reservation limits.

AG/fsblock reaping:
- `xrep_reap_agblocks` walks AG-block bitmaps for per-AG metadata.
- `xrep_reap_fsblocks` walks fsblock bitmaps for file metadata-like extents not directly from an inode fork.
- `xrep_reap_metadir_fsblocks` handles old btree blocks from metadata directory files and then resets metafile reservation accounting.

Extent selection:
- `xreap_agextent_select` and realtime equivalent split extents into runs with the same crosslink status.
- Crosslinked extents have this owner’s rmap/refcount removed but are not freed.
- Non-crosslinked extents are buffer-invalidated and freed.
- AGFL blocks are returned one at a time through `xreap_put_freelist`.

Buffer invalidation:
- `xrep_bufscan_max_sectors` and `xrep_bufscan_advance` scan for incore buffers of plausible sizes.
- `xreap_agextent_binval` invalidates AG metadata buffers.
- `xreap_bmapi_binval` invalidates buffers for inode fork mappings, accounting for possible larger directory/xattr buffers.
- Oversized/unloggable buffers are staled directly instead of logged for invalidation.

Transaction pressure:
- Reaping computes limits from log reservation costs for EFI/RUI/CUI/BUI and buffer invalidation items.
- It finishes deferred chains or rolls transactions before reservation exhaustion.
- Different limit calculators handle AG metadata, AG CoW, realtime CoW, and inode fork mappings.

Realtime support:
- Under `CONFIG_XFS_RT`, `xrep_reap_rtblocks` reaps realtime CoW staging extents with rtgroup locks and realtime rmap/refcount semantics.

Inode fork reaping:
- `xrep_reap_ifork` walks all real extents in a target/temp inode fork and reaps them.
- `xreap_bmapi_select` uses per-offset rmap owner info to split crosslinked/non-crosslinked portions.
- `xrep_reap_bmapi_iter` unmaps crosslinked fork mappings without freeing blocks, or unmaps and frees non-crosslinked blocks while updating quota block counts.

This file is central to safe cleanup after repair of btrees, xattrs, directories, CoW forks, and temporary exchange operations.
