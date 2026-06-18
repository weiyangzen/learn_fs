# File Research: sources/os/linux/linux/fs/ocfs2/journal.h

`journal.h` defines OCFS2 journaling state, recovery map structures, transaction APIs, metadata access wrappers, checkpoint helpers, and journal credit formulas.

Main contents:
- Defines `enum ocfs2_journal_state`: free, loaded, and shutdown.
- Defines `struct ocfs2_recovery_map`, a flexible array of node numbers pending recovery.
- Defines `struct ocfs2_journal`, wrapping JBD2 journal state plus OCFS2-specific inode, dinode buffer, transaction count, transaction barrier, checkpoint wait queue, local-alloc cleanup list, and recovery work item.
- Declares `trans_inc_lock` and inline helpers for:
  - Incrementing OCFS2 transaction IDs without wrapping to zero.
  - Recording a cache object’s last transaction.
  - Testing whether a metadata cache object is fully checkpointed.
  - Tracking whether a cache object/inode is still “new”.
- Declares orphan scan, recovery lifecycle, replay slot, journal lifecycle, dead-node marking, mount/quota recovery completion, and recovery-thread APIs.
- Defines `ocfs2_start_checkpoint()` and `ocfs2_checkpoint_inode()`, which wakes the commit thread and waits until an inode metadata cache is fully checkpointed on clustered mounts.
- Declares transaction APIs: start, commit, extend, assure credits, and allocation-oriented extension.
- Defines journal access types: create, write, undo.
- Declares typed metadata access wrappers for dinodes, extent blocks, refcount blocks, group descriptors, xattr blocks, quota blocks, directory blocks, dx roots, dx leaves, and non-ECC buffers.
- Documents the journal access/dirty protocol: a buffer must receive access before being dirtied.
- Defines metadata credit constants and calculators for inode updates, xattr updates, quota writes/sync, group extend/add, suballocator alloc/free, inline-to-extents conversion, truncate log updates, directory operations, mknod, local alloc window moves, link/unlink/rename, xattr block creation, dx root removal, refcount tree changes, extent extension, symlink creation, group allocation, and discontiguous block groups.
- Provides wrappers for JBD2 ranged inode writes, ordered truncate, and inode fsync transaction tracking.

This header is used widely by allocation, directory, inode, xattr, refcount, truncate, and ioctl paths to size transactions and safely modify metadata.
