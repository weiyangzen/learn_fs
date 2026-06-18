# File Research: sources/os/linux/linux-stable/fs/ubifs/gc.c

## Role

Implements UBIFS out-of-place garbage collection for both data and index LEBs. Data LEB GC copies live nodes into the GC journal head and frees the old LEB. Index LEB GC dirties corresponding TNC index nodes and delays physical reuse until after a commit.

## Core Flow

`ubifs_garbage_collect()` is the public GC loop. It:

- Requires the commit semaphore to be held by the caller.
- Checks whether commit is already needed and returns `-EAGAIN`.
- Locks the GC head write-buffer.
- Finds candidate dirty/freeable LEBs through `ubifs_find_dirty_leb()`.
- Calls `ubifs_garbage_collect_leb()` until it frees a usable LEB, needs commit, or gives up with `-ENOSPC`.
- Uses soft and hard LEB movement limits to prevent endless GC work.

`ubifs_garbage_collect_leb()` handles the selected LEB:

- Immediately unmaps LEBs whose space is entirely free/dirty and reserves one as `c->gc_lnum` if needed.
- Scans non-empty LEBs with `ubifs_scan()`.
- If the first node is an index node, dirties every index node in the TNC and queues the LEB on `c->idx_gc`.
- Otherwise sorts live data and metadata nodes and moves them to the GC head.

## Data LEB GC

`sort_nodes()` removes obsolete nodes via `ubifs_tnc_has_node()`, splits data from non-data nodes, and sorts:

- Data nodes by inode number then block number for bulk-read locality.
- Inode nodes before direntry/xentry nodes.
- Inode nodes by descending size.
- Direntry/xentry nodes by parent inode and hash.

`move_nodes()` writes live nodes into the GC head using first-fit placement. It preserves data-node ordering, opportunistically packs non-data nodes, updates authentication hashes when enabled, appends auth nodes, and switches GC heads when the current LEB cannot fit more useful nodes.

`move_node()` writes one scanned node through the GC wbuf and replaces its TNC location with `ubifs_tnc_replace()`.

## Index LEB GC

Index LEBs cannot be reused immediately because old index nodes may be needed for recovery. The file:

- Calls `ubifs_dirty_idx_node()` for each scanned index node.
- Records the LEB in `c->idx_gc`.
- Changes lprops to free space but removes `LPROPS_INDEX`.
- Returns `LEB_FREED_IDX`, making the caller continue or require commit.

`ubifs_gc_start_commit()` and `ubifs_gc_end_commit()` complete this delayed reuse by marking eligible index LEBs and unmapping them after commit safety is established.

## Safety and Recovery

`gc_sync_wbufs()` synchronizes all non-GC write-buffers before unmapping freeable LEBs, preventing loss of newer nodes that obsolete data in the LEB being erased.

The data path updates `c->gced_lnum` and increments `c->gc_seq` with memory barriers after moving nodes, allowing TNC lookups to detect races with GC relocation.

Errors other than expected `-EAGAIN`/`-ENOSPC` put UBIFS into read-only mode.

## Research Notes

This file is the bridge between lprops candidate selection, TNC liveness, journal write-buffer mechanics, and commit-time recovery rules. The distinction between data LEBs and index LEBs is central: data can be copied immediately, while index reclamation is staged through commit.
