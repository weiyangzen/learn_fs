# File Research: sources/os/linux/linux/fs/jffs2/erase.c

This file manages eraseblock erasure, erase verification, clean-marker writing, bad-block handling, and raw node-ref cleanup for erased blocks.

`jffs2_erase_pending_blocks()` drains `erase_complete_list` and `erase_pending_list` up to a requested count. Completed erases are moved to `erase_checking_list` and verified/marked by `jffs2_mark_erased_block()`. Pending blocks are removed from their list, accounting is moved from used/dirty/free/wasted into `erasing_size`, node refs are freed, and `jffs2_erase_block()` is invoked.

`jffs2_erase_block()` calls `mtd_erase()` on Linux. Allocation failures or transient erase errors refile the block to `erase_pending_list`; permanent failures call `jffs2_erase_failed()`. Successful erase moves the block to `erase_complete_list`, triggers GC, and wakes erase waiters.

`jffs2_erase_failed()` may update NAND bad-block information when cleanmarkers live in OOB and a specific bad offset is known. Blocks that should not be retried are moved to `bad_list`, with global erasing/bad accounting updated.

`jffs2_free_jeb_node_refs()` walks a block’s raw-node-ref blocks, removes refs from each inode/xattr ref chain with `jffs2_remove_node_refs_from_ino_list()`, frees refblocks, and clears `first_node`/`last_node`. This is required before reusing an eraseblock.

`jffs2_block_check_erase()` verifies a newly erased block contains all `0xff`, using `mtd_point()` where possible or page-sized reads otherwise. `jffs2_mark_erased_block()` then writes an OOB or in-band cleanmarker if needed, resets free accounting, links an in-band cleanmarker ref, moves the block to `free_list`, and updates free/erasing block counts.

Key dependencies: MTD erase/read/point APIs, NAND cleanmarker and badblock helpers from writebuffer code, node-ref helpers in `nodelist.c`, and GC trigger/wait mechanisms.

Important invariants: eraseblock list transitions are protected by `erase_free_sem` plus `erase_completion_lock`; a block is only returned to `free_list` after erase verification and cleanmarker handling.
