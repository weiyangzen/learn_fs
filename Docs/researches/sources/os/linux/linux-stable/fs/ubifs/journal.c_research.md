# File Research: sources/os/linux/linux-stable/fs/ubifs/journal.c

## Role

Implements UBIFS journal mutation paths. The journal consists of fixed-position log LEBs and variable bud LEBs. The log records references to buds; buds contain data, inode, dent, xent, truncate, and related nodes that become indexed after commit.

## Reservation and Write Pipeline

`make_reservation()` is the central reservation loop:

- Waits if reservation queuing is active.
- Takes `commit_sem` for reading.
- Calls `reserve_space()` for a journal head.
- Runs GC and commit on `-ENOSPC`/`-EAGAIN`.
- Starts serialized queuing if many concurrent reservers repeatedly race for freed space.
- Leaves the journal head locked and commit semaphore held on success.

`reserve_space()` checks the current head wbuf, finds free LEB space, runs GC if needed, syncs the previous wbuf before logging a new bud, adds the bud to the log, and seeks the wbuf.

`write_head()` writes prepared grouped nodes to a journal head and optionally syncs it. When authentication is enabled, it hashes all nodes in the group and prepares an auth node at the end.

`release_head()` unlocks the wbuf. `finish_reservation()` releases `commit_sem`.

## Node Packing

The file packs on-flash nodes for journal operations:

- `pack_inode()` serializes inode metadata, flags, xattr stats, size, timestamps, ownership, compression, and attached data unless the inode is being deleted.
- `zero_*_unused()` clears unused padding fields in inode, dent, and truncate nodes.
- `get_dent_type()` translates inode mode to UBIFS direntry type.
- `set_dent_cookie()` adds a random cookie when double-hash direntries are enabled.

## Metadata Updates

`ubifs_jnl_update()` atomically writes a dent/xent node, target inode, and parent/host inode. It handles create/link/unlink/rmdir/xattr-entry updates, orphan insertion for last-reference deletions, TNC insertion/removal, dirt accounting, inode clean marking, and sync behavior for synchronous parent or target inodes.

`ubifs_jnl_write_inode()` flushes a single inode. For deletion it may also write deletion inodes for hosted xattrs and remove the inode from the TNC/orphan tracking. `ubifs_jnl_delete_inode()` optimizes final inode deletion by avoiding a second deletion inode if no commit occurred since orphaning.

## Data Updates

`ubifs_jnl_write_data()` writes one data node:

- Allocates a compressed data buffer or falls back to the reserved write buffer.
- Chooses compression based on inode flags.
- Compresses folio data.
- Encrypts if needed.
- Reserves DATAHD space, writes the node, calculates hash, tracks inode in the wbuf, and adds the TNC entry.

## Rename Paths

`ubifs_jnl_xrename()` implements exchange rename by writing two dent nodes and one or two parent inode nodes.

`ubifs_jnl_rename()` handles normal rename, cross-directory moves, replacement of an existing target, whiteout creation, orphan insertion for replaced last-reference targets, old dent removal or replacement, and TNC updates for all affected inodes.

Both functions group all nodes into one journal write so replay can drop incomplete groups after an unclean reboot.

## Truncate and Xattrs

`ubifs_jnl_truncate()` writes an inode node, truncation node, and possibly a recompressed/re-encrypted last data node. It updates TNC for the shortened final block, removes data-key ranges beyond the new size, and accounts the truncation node as dirty.

`truncate_data_node()` handles the last-block rewrite by decrypting, decompressing, recompressing, and re-encrypting as needed.

`ubifs_jnl_delete_xattr()` writes deletion xentry, deletion xattr inode, and updated host inode, then removes xattr records from TNC.

`ubifs_jnl_change_xattr()` writes updated host and xattr inode nodes, preserving the rule that host inode sync also flushes its xattr inode changes.

## Failure Handling

Most journal mutation failures after media/TNC modification call `ubifs_ro_mode()`. Orphan additions are rolled back when the grouped write fails before completion. Budgeted dirty inodes are marked clean only after successful TNC updates and reservation completion.

## Research Notes

This is the main consistency engine for UBIFS namespace, inode, xattr, truncate, and data writes. It depends tightly on `io.c` write-buffer semantics, `log.c` bud registration, `gc.c` space reclamation, `key.h` key construction, and TNC operations for logical indexing.
