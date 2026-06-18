# File Research: sources/os/bsd/dragonflybsd/sys/vfs/hammer/hammer_cursor.h

## Role

Defines the `hammer_cursor` structure and cursor flags used by HAMMER B-tree lookup, iteration, insertion, pruning, reblocking, mirroring, and in-memory/on-disk record merge scans.

## Main Data Structures

- `struct hammer_cursor` stores the active transaction, parent/current B-tree nodes, node indices, deadlock recovery references, key range, B-tree bounds, data/leaf pointers, flags, inode context, and current in-memory record.
- `struct hammer_cmirror` extends cursor scans with a `mirror_tid` filter and skipped internal-node bounds for mirror optimization.

## Important Fields

- `parent`, `parent_index`, `node`, and `index` identify the current B-tree position.
- `left_bound` and `right_bound` represent inherited node bounds; the right bound is range-exclusive.
- `key_beg`, `key_end`, and `asof` define lookup or iteration constraints.
- `data_buffer`, `leaf`, and `data` expose extracted on-disk or in-memory record payloads.
- `ip` and `iprec` connect cursors to inode-local merged scans.
- `deadlk_node` and `deadlk_rec` allow cleanup or recovery paths to wait for deadlocked nodes/records after releasing normal cursor state.

## Flag Groups

- Extraction/control flags include `HAMMER_CURSOR_GET_DATA`, `HAMMER_CURSOR_BACKEND`, `HAMMER_CURSOR_INSERT`, and delete visibility controls.
- Iteration state flags include `ATEDISK`, `ATEMEM`, `DISKEOF`, `MEMEOF`, `RETEST`, and `LASTWASMEM`.
- Snapshot and mirroring flags include `ASOF`, `CREATE_CHECK`, and `MIRROR_FILTERED`.
- Maintenance flags include `PRUNING`, `REBLOCKING`, `TRACKED`, `TRACKED_RIPOUT`, `ITERATE_CHECK`, and `NOSWAPCACHE`.

## Helper Macros

- `hammer_cursor_inmem(cursor)` tests whether the current leaf comes from the cursor’s in-memory record.
- `hammer_cursor_ondisk(cursor)` is the inverse condition, identifying on-disk B-tree state.

## Research Notes

The header documents an important design rule: cursors are tracking structures, and unrelated B-tree operations may modify them while they are not holding exclusive node locks. This is the contract implemented by `hammer_cursor.c`.
