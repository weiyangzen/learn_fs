# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/iscan.c

This file implements live filesystem inode scanning for scrub and repair modules that need to visit every allocated inode while concurrent updates may occur.

Core model:
- The scanner walks allocated inodes from the inobt while holding AGI during cursor advancement.
- It records a scan start, current cursor, visited cursor, skipped inode mask, and batched inode references.
- Callers pair scanning with live update hooks and use `xchk_iscan_want_live_update` to decide whether an update applies to already-scanned ranges.

Cursor advancement:
- `xchk_iscan_find_next` uses an inobt cursor to find the next allocated inode after the scan cursor, masks `skip_ino`, and returns an allocation mask for a chunk.
- `xchk_iscan_move_cursor` updates scan and visited cursors while holding the scanner mutex.
- `xchk_iscan_advance` reads AGI, finds the next inode, wraps across AGs, and marks the scan finished when it returns to the start.
- `xchk_iscan_finish` and `xchk_iscan_finish_early` mark all future updates as applicable.

Inode acquisition:
- `xchk_iscan_read_agi` optionally trylocks AGI with retry timing.
- `xchk_iscan_iget` gets the first inode and then attempts to batch up to a chunk of consecutive allocated inodes with no-retry/dontcache flags.
- `xchk_iscan_iget_retry` backs up the cursor after transient iget failures, optionally pushing or flushing inodegc.
- `xchk_iscan_iter_batch` advances and fills a batch.
- `xchk_iscan_iter` hands one inode reference to the caller.
- `xchk_iscan_iter_finish` drops leftover batched references.

Live update selection:
- `xchk_iscan_mark_visited` marks an inode fully scanned.
- `xchk_iscan_finish_batch` advances visited state over skipped unallocated inodes.
- `xchk_iscan_skipped` identifies newly allocated inodes skipped in the current batch.
- `xchk_iscan_want_live_update` returns true for finished scans, skipped inodes, or inodes within the already visited range, handling wraparound.

Startup and teardown:
- `xchk_iscan_start` chooses a rotating AG start point, initializes timing, state, mutex, cursors, and batch slots.
- `xchk_iscan_teardown` releases batched references, marks finished, and destroys the mutex.

Important invariants:
- Cursor advancement under AGI prevents inode create/delete races across the advanced range.
- Callers must hold adequate inode locks before calling `xchk_iscan_mark_visited`.
- Skipped unallocated inodes must receive live updates because they can be allocated after the batch snapshot.

Risks and edge cases:
- Inodegc races can cause temporary `-EAGAIN`, `-ENOENT`, or `-EBUSY`.
- Trylock AGI mode lets repair avoid deadlocks when already holding locks such as AGI elsewhere.
- Aborted scans suppress live updates.
