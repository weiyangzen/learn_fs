# File Research: sources/virtualization/qemu/block/copy-before-write.c

Implements the `copy-before-write` block filter used by backup/fleecing flows. It sits above a source node and copies old data into a target before guest writes, discards, or write-zeroes modify the source.

`BDRVCopyBeforeWriteState` owns a `BlockCopyState`, target child, CBW error policy, timeout, discard-source flag, a coroutine mutex, an access bitmap for snapshot reads, a done bitmap for already copied areas, a request list for frozen snapshot reads, and `snapshot_error`. `cbw_do_copy_before_write()` aligns writes to the block-copy cluster size, starts `block_copy()`, handles timeout/error policy, marks copied clusters in `done_bitmap`, and waits for overlapping frozen snapshot read requests before allowing the guest write to proceed.

Normal reads pass through to `bs->file`; writes/discards/zeroes first call copy-before-write and then forward to the source. Snapshot reads use `cbw_snapshot_read_lock()` to verify requested areas are in `access_bitmap`, choose either `target` for already copied ranges or `bs->file` for protected source ranges, and block overlapping guest writes via `frozen_read_reqs`. Snapshot discard clears access bits, resets block-copy state, and discards from target.

`cbw_open()` parses QAPI-style options, opens `file` and `target`, optionally looks up a bitmap, creates `BlockCopyState`, creates disabled done/access bitmaps, initializes access from block-copy's dirty bitmap, and sets supported write/zero flags. `cbw_child_perm()` gives target write permission while controlling resize and source write/consistent-read permissions. `bdrv_cbw_append()` constructs options and inserts the filter; `bdrv_cbw_drop()` removes it. The driver registers as filter `copy-before-write`.
