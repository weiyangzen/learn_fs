# File Research: sources/os/linux/linux/fs/iomap/ioend.c

Implements iomap `ioend` allocation, writeback submission, completion, merging, sorting, splitting, and checkpoint-style finishing for buffered and direct I/O completions.

Key structures and globals:
- Exports `iomap_ioend_bioset`.
- `iomap_init_ioend()` initializes an `iomap_ioend` embedded in a bio with inode, offset, size, sector, flags, and refcount.

Buffered writeback:
- `iomap_add_to_ioend()` appends dirty folio ranges to the current writeback ioend when physical/logical contiguity, flags, integrity size, and batch limits allow it. Otherwise it submits the current ioend and allocates a new one.
- `iomap_ioend_writeback_submit()` sets the default buffered end-io handler, rejects anonymous writes in this path, generates integrity metadata when needed, and submits the bio.
- `iomap_finish_ioend_buffered_write()` handles writeback errors, reports `FSERR_BUFFERED_WRITE`, finishes folio writeback state, frees integrity payloads, and drops the bio.
- Failed buffered write completions are deferred through a global work item so fs error reporting does not recursively acquire locks from bio completion context.

Generic completion:
- `iomap_finish_ioend()` handles child split ioends, propagates errors, waits for all children via `io_remaining`, verifies read integrity, and dispatches to direct, buffered read, or buffered write finishers.
- `iomap_finish_ioends()` finishes a possibly merged list in task context and yields after large batches.

Merging and sorting:
- `iomap_ioend_can_merge()` allows adjacent write ioends to merge only if status, flags, logical offsets, and physical sectors match.
- `iomap_ioend_try_merge()` chains mergeable ioends behind one head.
- `iomap_sort_ioends()` sorts by file offset.

Splitting:
- `iomap_split_ioend()` splits write ioends for max length or zone append limits, aligns the split to filesystem block size, creates a child ioend, increments parent remaining count, and updates offsets/sectors.

Initialization:
- `iomap_ioend_init()` initializes the bioset at `fs_initcall`.

This file is the bridge between iomap folio writeback/direct I/O and block-layer bio completion, with careful batching to limit completion latency.
