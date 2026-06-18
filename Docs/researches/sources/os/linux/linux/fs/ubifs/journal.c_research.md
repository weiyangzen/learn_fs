# File Research: sources/os/linux/linux/fs/ubifs/journal.c

## Purpose

`journal.c` implements UBIFS journal write operations for metadata, data, directory operations, truncation, inode deletion, and xattrs. UBIFS uses a multi-headed journal: the base head stores inode, direntry, xentry, and truncation nodes, while data heads store data nodes. Journal operations reserve space, write grouped nodes atomically with respect to recovery, update the TNC, manage orphan state, and mark inodes clean.

## Reservation and Write Pipeline

`reserve_space()` locks a journal head write-buffer, checks available space, finds free space through lprops, invokes GC on `-ENOSPC`, syncs the previous write-buffer before adding a new bud to the log, writes the bud reference with `ubifs_add_bud_to_log()`, and seeks the head to the selected LEB. It can return `-EAGAIN` when commit is required.

`make_reservation()` wraps `reserve_space()` with `commit_sem` read locking and retry logic. It converts GC `-ENOSPC` to commit/retry behavior, runs `ubifs_run_commit()` on `-EAGAIN`, and after many retries starts serializing reservation contenders through `reserve_space_wq` using `wait_for_reservation()`, `add_or_start_queue()`, and `wake_up_reservation()`. `release_head()` unlocks the write-buffer; `finish_reservation()` releases the commit read lock.

`write_head()` records the current LEB/offset, hashes nodes for authenticated mounts, writes through `ubifs_wbuf_write_nolock()`, and optionally synchronizes the write-buffer. `ubifs_hash_nodes()` walks grouped nodes and appends an auth node when authentication is enabled.

## Node Packing and Clean Accounting

`pack_inode()` serializes VFS and UBIFS inode state into an on-flash inode node, optionally omitting attached data when writing a deletion inode. Small helpers zero unused node fields for deterministic on-flash contents. `mark_inode_clean()` clears UBIFS dirty state and releases dirty-inode budget. `set_dent_cookie()` supplies a random cookie for double-hash directory entries.

## Major Journal Operations

`ubifs_jnl_update()` writes a dent/xent node, the target inode, and the parent/host inode as one grouped update. It handles deletion dentries, xattr ordering, synchronous inode/dirsync flushes, orphan insertion for last references, and TNC add/remove updates.

`ubifs_jnl_write_data()` compresses a folio block when enabled, encrypts it when needed, writes the data node on the data head, calculates the node hash, tracks the inode in the write-buffer, and adds the TNC entry. It falls back to `c->write_reserve_buf` under memory pressure so writeback can still proceed.

`ubifs_jnl_write_inode()` writes an inode to the base head, optionally writing deletion records for hosted xattrs. If the inode's last reference is gone, it removes all TNC records for that inode and deletes orphan state. `ubifs_jnl_delete_inode()` avoids writing a second deletion inode when no commit has happened since unlink and the inode has no xattrs.

`ubifs_jnl_xrename()` handles exchange rename by writing two dentries and one or two parent inodes. `ubifs_jnl_rename()` handles regular rename, replacement, whiteout, cross-directory movement, orphan insertion for replaced inodes, TNC updates/removals, and optional whiteout orphan deletion.

`ubifs_jnl_truncate()` writes an inode node and truncation node, and if the new size splits an existing final data block it reads, decompresses/decrypts, truncates, recompresses/reencrypts, and writes that data node. It removes the truncated data-key range from the TNC.

`ubifs_jnl_delete_xattr()` writes deletion xentry, deletion inode, and updated host inode, then removes xentry and xattr inode ranges from the TNC. `ubifs_jnl_change_xattr()` writes the host inode and xattr inode, ordered so syncing the host also flushes the xattr change.

## Invariants and Failure Behavior

Space reservation must happen before sequence numbers are allocated. Grouped writes use node group markers so recovery can discard incomplete multi-node updates. TNC updates occur only after journal data is written. Errors after journal write generally switch UBIFS to read-only because journal/TNC divergence is dangerous. Authenticated mounts add auth-node space to reservations and mark auth nodes dirty in lprops.
