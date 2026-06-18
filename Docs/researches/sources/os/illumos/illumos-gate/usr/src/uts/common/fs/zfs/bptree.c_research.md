# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/bptree.c

## Scope

Implements ZFS bptrees: persistent queues of root block pointers for destroyed datasets whose block trees are freed asynchronously by sync-time scanning.

Read completely: 302 lines.

## Core Model

A bptree object stores `bptree_entry_phys_t` records in object data and `bptree_phys_t` queue/accounting state in the bonus buffer. `bt_begin` and `bt_end` form a monotonically increasing queue window and reset only when the object is destroyed and recreated.

## Main APIs

- `bptree_alloc()` allocates and initializes a bptree object.
- `bptree_free()` asserts the queue and accounting are empty, then frees the object.
- `bptree_is_empty()` checks `bt_begin == bt_end`.
- `bptree_add()` appends a destroyed dataset root block pointer plus birth txg and space accounting.
- `bptree_iterate()` traverses queued destroyed dataset trees, optionally freeing blocks and recording progress.

## Control Flow

`bptree_add()` runs only in syncing context, writes a new entry at `bt_end`, increments `bt_end`, and updates byte/compressed/uncompressed counters.

`bptree_iterate()` holds the bonus buffer, optionally dirties it for freeing, then scans entries from `bt_begin` to `bt_end`. Each entry is traversed via `traverse_dataset_destroyed()` using `bptree_visit_cb()` to invoke the caller block-pointer function.

When freeing:

- Successful traversal advances `bt_begin` and frees the processed entry range.
- Nonzero traversal errors save the bookmark for resume.
- I/O-like errors (`EIO`, `ECKSUM`, `ENXIO`) can be recorded while continuing to later entries.
- If previous I/O errors prevent advancing `bt_begin`, later completed entries are marked no-op with `be_birth_txg = UINT64_MAX`.

If `zfs_free_leak_on_eio` is set, traversal uses `TRAVERSE_HARD` and final accounting may be zeroed when all entries are logically complete.

## Dependencies

Depends on DMU object/bonus/data operations, destroyed-dataset traversal, block accounting helpers, DSL pool scan/free behavior, sync-context transactions, ZFS debug logging, and global `zfs_free_leak_on_eio`.

## Invariants And Risks

- Freeing requires a syncing transaction.
- `bt_bytes`, `bt_comp`, and `bt_uncomp` must reach zero when all entries are complete.
- Bookmarks allow resumable destruction after errors or partial processing.
- I/O error policy differs between free and nofree traversal.
- The queue counters are monotonic within one object lifetime; consumers must not assume wraparound reset except after object recreation.
