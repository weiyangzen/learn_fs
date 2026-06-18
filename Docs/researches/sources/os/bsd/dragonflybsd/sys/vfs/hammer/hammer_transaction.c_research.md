# File Research: sources/os/bsd/dragonflybsd/sys/vfs/hammer/hammer_transaction.c

Purpose: manages lightweight HAMMER transaction setup/teardown and allocates transaction/object identifiers.

Transactions: `hammer_start_transaction()` creates a standard transaction with a referenced root volume, timestamp fields, and no TID until one is needed. `hammer_simple_transaction()` creates a read-only transaction with the same timestamp/root-volume setup. `hammer_start_transaction_fls()` is for the flusher thread, preallocates a TID, and starts with one sync-lock reference to reflect flusher serialization. `hammer_done_transaction()` releases the root volume, asserts expected sync-lock references, and waits for inode reclaim work when new inodes were created.

TID allocation: `hammer_alloc_tid()` normally advances `hmp->next_tid` linearly. In master-id mode it aligns allocations to `HAMMER_MAX_MASTERS` and ORs in the master id so transaction ids can be partitioned by master. The file notes HAMMER1 no longer supports multi-master clustering as of 2015, but the encoding remains.

Object-id allocation: `hammer_alloc_objid()` maintains a per-directory object-id cache. It allocates a bulk TID range, chooses a bit based on high bits of the directory entry namekey, and frees or recycles caches based on fill level. The goal is to distribute inode numbers while preserving some relation to directory-entry hash space.

Cache helpers: `ocp_allocbit()` finds and marks an available bit in the two-level bitmap. `hammer_clear_objid()` detaches a directory's cache and moves it to the front of the mount list. `hammer_destroy_objid_cache()` frees all object-id caches during mount teardown.

Research notes: transactions here are not heavyweight journaling objects; the actual persistence mechanism is the sync lock plus UNDO/REDO FIFO. This file supplies the monotonic identifiers that version HAMMER records and object ids.
