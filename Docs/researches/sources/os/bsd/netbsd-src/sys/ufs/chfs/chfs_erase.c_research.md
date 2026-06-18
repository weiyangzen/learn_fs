# File Research: sources/os/bsd/netbsd-src/sys/ufs/chfs/chfs_erase.c

Purpose: Implements eraseblock remapping for CHFS logical eraseblocks. This is the low-level transition from an erasable/dirty block back to a free block after EBH unmap/map.

Key entry point:
- `chfs_remap_leb(struct chfs_mount *chmp)`: selects an erase-pending block, frees its node-reference blocks, calls `chfs_unmap_leb` and `chfs_map_leb`, resets per-block and mount accounting, and returns the block to `chm_free_queue`.

Important behavior:
- Requires `chm_lock_mountfields` and `chm_lock_sizes`; asserts write buffer lock is not held.
- If no blocks are directly erasable, it can promote one block from `chm_erasable_pending_wbuf_queue` after flushing pending write-buffer data.
- Resets `dirty`, `unchecked`, `used`, `free`, and `wasted` accounting through the shared size-change helpers.
- On success, the eraseblock has `first_node` and `last_node` cleared and is inserted into `chm_free_queue`.

Dependencies:
- EBH mapping functions from the CHFS/flash layer.
- Node-ref lifecycle from `chfs_malloc.c`.
- Size accounting and queues from `chfs_vnode.c` and mount state.

Research notes:
- Comments still mark remap policy as needing more design.
- ENOSPC is returned if neither erase-pending nor pending-wbuf erasable blocks are available.
- Error paths after unmap/map do not restore the block to a queue in this file.
