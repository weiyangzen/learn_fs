# File Research: sources/os/linux/linux-stable/fs/jffs2/jffs2_fs_sb.h

## Role

Defines JFFS2 private superblock state and mount options.

## Mount Options

`struct jffs2_mount_opts` stores:

- compression override flag and selected compression mode;
- reserved-pool size flag and value, limiting non-root writes when free space drops below the pool.

## Superblock State

`struct jffs2_sb_info` contains:

- MTD device pointer.
- Highest inode and next inode-to-check counters.
- superblock flags: read-only, scanning, building.
- GC task pointer and start/exit completions.
- `alloc_sem`, protecting allocation, write ordering, and GC-critical fields.
- flash geometry and global accounting:
  - flash, sector, used, dirty, wasted, free, erasing, bad, unchecked sizes;
  - number of free and erasing blocks.
- reserved-block thresholds for writes, deletions, GC triggering, bad-block GC, and GC merging.
- eraseblock array, current write block, and current GC block.
- block lists:
  - clean, very dirty, dirty, erasable, erasable pending writebuffer, erasing, erase checking, erase pending, erase complete, free, bad, and bad-used.
- erase locking and wait queue.
- inode cache hash table, lock, and wait queue.
- `erase_free_sem` for safe erase/ref freeing coordination.
- write-buffer fields when configured:
  - write buffer, offset/length, dirty inode list, rwsem, delayed work, OOB buffer/space, optional verify buffer.
- summary subsystem pointer.
- xattr indexes/lists/semaphores/counters when configured.
- `os_priv` back pointer to the OS superblock.

## Research Notes

This header shows that JFFS2’s superblock is primarily a flash-space and GC ledger. Most high-level operations ultimately update these counters and lists through allocation, node-ref, erase, or GC paths.
