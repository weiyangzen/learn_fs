# File Research: sources/os/bsd/netbsd-src/sys/ufs/chfs/chfs_build.c

Read completely: 371 lines.

Builds CHFS's in-memory filesystem representation during mount. It computes GC/reservation thresholds, scans eraseblocks, constructs vnode-cache link counts from scanned directory entries, removes unlinked vnode subtrees, frees scan-only dirents, and initializes the write-buffer offset.

Trigger setup:
- `chfs_calc_trigger_levels` reserves two blocks for deletions.
- Write reservation is deletion reservation plus about 2% of flash size, plus 100 bytes per physical eraseblock, rounded to eraseblock size.
- GC trigger, GC merge, very-dirty trigger, and dirty-space ENOSPC thresholds are derived from eraseblock and flash sizes.

Link reconstruction:
- `chfs_build_set_vnodecache_nlink` walks a vnode cache's `scan_dirents`.
- Missing child vnode caches cause the dirent node to be marked obsolete and removed.
- Directory child links set `pvno` and ensure at least one link, while duplicate directory parents are reported as hard links.
- Both child and parent link counts are incremented for live entries.

Unlinked removal:
- `chfs_build_remove_unlinked_vnode` requires `chm_lock_mountfields`.
- It marks all data nodes, dirent nodes, and vnode nodes obsolete, resets each node-ref list back to the vnode-cache sentinel, and clears non-root vnode state to unchecked.
- Scan dirents are removed; child link counts are decremented, and newly linkless children are queued for cascading removal.

Mount build pass:
- `chfs_build_filesystem` runs under `chm_lock_mountfields`.
- Step 1 marks scanning, initializes each eraseblock, skips unmapped LEBs into the free queue, scans mapped eraseblocks, and queues them as free, clean, selected nextblock, closed dirty, or erase-pending depending on scan classification.
- Step 2 marks building and walks every vnode-cache bucket to compute parent/link relationships from scan dirents.
- Step 3 removes vnode caches with zero link count, then drains the cascading unlinked dirent queue.
- Final cleanup frees all remaining scan dirents, removes `vno == 0` refs, marks directory child vnode caches present, asserts scan lists empty, and initializes `chm_wbuf_ofs` from the chosen nextblock or `0xffffffff`.

Risks and notes:
- The file has TODO comments for bad-block handling during erase/write/read and uncertainty about unlinked-list insertion order.
- In the final cleanup path, `notregvc = chfs_vnode_cache_get(...)` is dereferenced without a null check for directory entries with nonzero `vno`.
- Some unknown scan states fall through the default case without changing `err`, so scan error propagation depends on scan return conventions.
