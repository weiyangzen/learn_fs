# File Research: sources/os/bsd/dragonflybsd/sys/vfs/hammer/hammer_cursor.c

## Role

Implements HAMMER B-tree cursor lifecycle, navigation, lock upgrading/downgrading, deadlock recovery, and live cursor adjustment during B-tree mutation. A `hammer_cursor` is not just an iterator; it is a tracked mutable handle that other B-tree maintenance operations may adjust while the cursor is unlocked.

## Major Entry Points

- `hammer_init_cursor()` initializes a cursor from an optional node cache or the filesystem root B-tree node, with throttling for frontend readers when the backend flusher is under reclaim pressure.
- `hammer_done_cursor()` releases parent/node/data/inode/memory-record references and waits out deadlock recovery references.
- `hammer_normalize_cursor()` repairs cursors left with `node == NULL` by moving up to the parent.
- `hammer_cursor_upgrade()`, `hammer_cursor_upgrade_node()`, `hammer_cursor_downgrade()` handle shared-to-exclusive lock transitions.
- `hammer_cursor_upgrade2()` and `hammer_cursor_downgrade2()` upgrade/downgrade two cursors while accounting for shared nodes, used by deduplication.
- `hammer_cursor_seek()`, `hammer_cursor_up()`, `hammer_cursor_up_locked()`, and `hammer_cursor_down()` reposition cursors in the B-tree.
- `hammer_unlock_cursor()`, `hammer_lock_cursor()`, and `hammer_recover_cursor()` implement tracked unlock/relock deadlock recovery.
- Mutation callbacks such as `hammer_cursor_replaced_node()`, `hammer_cursor_removed_node()`, `hammer_cursor_split_node()`, `hammer_cursor_moved_element()`, `hammer_cursor_parent_changed()`, `hammer_cursor_deleted_element()`, and `hammer_cursor_inserted_element()` keep unlocked tracked cursors coherent across B-tree restructuring.
- `hammer_push_cursor()` and `hammer_pop_cursor()` duplicate/restore a cursor for nested operations.
- `hammer_cursor_invalidate_cache()` drops cached data buffers before underlying storage is freed or repointed.

## Implementation Notes

- Cursor initialization may delay non-flusher transactions via time-domain multiplexing when reclaimed inode pressure is high and the flusher is running.
- Cursor parent information is loaded through `hammer_load_cursor_parent()`, which also establishes left/right B-tree bounds from parent elements or root sentinels.
- Lock upgrades record failed nodes in `deadlk_node`; cleanup later waits on that node so retry loops do not race immediately back into the same deadlock.
- Tracked cursors are inserted into `node->cursor_list` while unlocked. B-tree structural operations walk those lists and adjust cursor node references, indices, and leaf pointers.
- A removed element sets `HAMMER_CURSOR_TRACKED_RIPOUT`; relocking clears `ATEDISK` and sets `RETEST` so iteration does not skip the successor.
- Node removal during recovery can set `HAMMER_CURSOR_ITERATE_CHECK`, explicitly telling iteration code the cursor may now sit outside the original search range.
- `hammer_cursor_moved_element()` has special handling for cursors pointing at parent separators when a first child element moves, preventing mirror/write iteration from losing its place.
- Data buffer invalidation is important because cached cursor buffers can prevent buffer-cache invalidation when deduplication or block freeing changes the underlying block.

## Dependencies

Uses HAMMER node refs/locks, B-tree parent lookup, root volume lookup, node cache refs, transaction state, inode locks, memory-record refs, flusher pressure state, and TAILQ cursor tracking on nodes.

## Research Notes

This file is central to HAMMER’s concurrent B-tree correctness. Its core invariant is that active cursors either hold node locks or are explicitly tracked so structural mutations can rewrite their location before they are relocked.
