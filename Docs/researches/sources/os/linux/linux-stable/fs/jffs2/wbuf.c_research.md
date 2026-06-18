# File Research: sources/os/linux/linux-stable/fs/jffs2/wbuf.c

This file implements JFFS2 write-buffer support for media that cannot support arbitrary byte writes, especially NAND, DataFlash, UBI volumes, and non-bitwriteable NOR.

Key responsibilities:
- Tracks which inodes have pending non-GC writes in the write buffer so GC/fsync can flush only relevant data when possible.
- Refiles eraseblocks that become erasable only after pending write-buffer data is flushed.
- Handles bad or suspect blocks with `jffs2_block_refile()`, moving them to `bad_used_list` or erase-pending state and accounting remaining space as obsolete/wasted.
- Verifies writes when `CONFIG_JFFS2_FS_WBUF_VERIFY` is enabled.
- Recovers from write-buffer flush failures in `jffs2_wbuf_recover()` by marking the failed block bad/obsolete, reading any partially written old data when possible, reserving new GC space, rewriting recoverable nodes, relinking raw refs, and updating in-core full dnode/dirent or xattr references.
- Flushes the write buffer in `__jffs2_flush_wbuf()`, optionally padding with dirty bytes or a padding node, writing exactly one write-buffer page, linking padding refs, refiling erasable-pending blocks, and clearing dirty-inode tracking.
- Exposes `jffs2_flush_wbuf_gc()` and `jffs2_flush_wbuf_pad()` for GC-triggered and pad-to-end flushes.
- Implements write-buffered `jffs2_flash_writev()` and `jffs2_flash_write()`, enforcing contiguous writes, splitting full-page direct writes from buffered tails, and feeding summary collection.
- Implements `jffs2_flash_read()` overlaying pending write-buffer bytes on top of MTD reads and tolerating ECC warning returns when the requested data was returned.
- Implements NAND OOB cleanmarker checks/writes, OOB-empty scans, and bad-block marking after repeated erase failures.
- Schedules delayed write-buffer flushing through `dirty_writeback_interval` and `system_long_wq`.
- Provides setup/cleanup for NAND, DataFlash, NOR write-buffer, and UBI volume modes, configuring cleanmarker size, sector size, write-buffer page size, OOB buffers, delayed work, and optional verify buffers.

Important interactions:
- Sits beneath all JFFS2 flash I/O when `jffs2_is_writebuffered(c)` is true.
- Coordinates with allocator/GC through `alloc_sem`, `wbuf_sem`, `erase_completion_lock`, raw-node-ref lists, and block lists.
- Recovery may fetch present inodes through GC helpers to patch live in-core raw-ref pointers.

Notable invariants and risks:
- Writes must be contiguous within the current eraseblock or start a new block; non-contiguous writes are fatal.
- Recovery is best-effort and logs possible data loss when old partial data or replacement space cannot be obtained.
- Pending write-buffer bytes must be visible to reads; otherwise freshly written nodes could fail CRC or appear absent.
- Summary is disabled for recovered blocks because recovery does not reconstruct collected summary state.
- OOB cleanmarker handling uses only the historical 8-byte cleanmarker prefix.
