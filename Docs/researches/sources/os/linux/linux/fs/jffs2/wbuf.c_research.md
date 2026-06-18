# File Research: sources/os/linux/linux/fs/jffs2/wbuf.c

## Role

Implements write-buffered flash I/O for NAND, DataFlash, UBI volumes, and write-buffered NOR. It handles page-aligned buffering, pending inode tracking, OOB cleanmarkers, bad-block handling, delayed flushes, and write-failure recovery.

## Key Responsibilities

- Tracks which inode writes are pending in the write buffer through `jffs2_wbuf_pending_for_ino()`, `jffs2_wbuf_dirties_inode()`, and `jffs2_clear_wbuf_ino_list()`.
- Refiles blocks whose erasure was delayed by dirty write-buffer contents via `jffs2_refile_wbuf_blocks()`.
- Moves failed or suspect blocks to bad/erase lists through `jffs2_block_refile()`.
- Recovers from write-buffer write failure in `jffs2_wbuf_recover()`, copying still-valid nodes to a new block and updating raw refs and in-core inode/xattr pointers.
- Flushes buffered pages in `__jffs2_flush_wbuf()`, optionally padding and accounting wasted space.
- Provides GC-triggered and pad-triggered flush entry points: `jffs2_flush_wbuf_gc()` and `jffs2_flush_wbuf_pad()`.
- Implements buffered vector writes in `jffs2_flash_writev()` and scalar writes in `jffs2_flash_write()`.
- Implements `jffs2_flash_read()` that overlays pending write-buffer bytes on top of MTD reads and tolerates ECC-corrected/raw-read cases for later CRC validation.
- Implements NAND OOB helpers: `jffs2_check_oob_empty()`, `jffs2_check_nand_cleanmarker()`, `jffs2_write_nand_cleanmarker()`, and `jffs2_write_nand_badblock()`.
- Schedules delayed write-buffer sync with `jffs2_dirty_trigger()`.
- Provides setup/cleanup for NAND, DataFlash, NOR write-buffered flash, and UBI volume modes.

## Important Interactions

- Serializes buffered reads/writes with `wbuf_sem`.
- Requires `alloc_sem` for flush paths that alter allocation/accounting.
- Uses `erase_completion_lock` for block-list and raw-ref changes.
- Calls allocator, GC, summary, raw-node-ref, xattr, and inode-fetch helpers.
- Summary collection is fed from `jffs2_flash_writev()` after successful writes.

## Invariants and Risks

- Buffered writes must be contiguous within an eraseblock or start a new block; non-contiguous writes trigger `BUG()`.
- Recovery updates both raw-node lists and in-core structures for present inodes.
- If recovery cannot reread partially written old data, earlier affected nodes may be lost and the code advances to recover later complete nodes.
- Pending-inode tracking intentionally degrades to “all dirty” on allocation failure.
- OOB cleanmarker behavior differs from inline cleanmarker behavior used on NOR/direct modes.
