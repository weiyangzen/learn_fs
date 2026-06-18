# File Research: sources/os/bsd/netbsd-src/sys/kern/kern_fileassoc.c

Read completely: 643 lines.

Implements `fileassoc(9)`, a per-mount facility for attaching subsystem-private data to files identified by filesystem file handles. It provides registration of association types, mount-local hash tables keyed by file handles, per-file specificdata storage, cleanup callbacks, and fast-path avoidance when no associations exist.

Core structures:
- `struct fileassoc` records an association name, cleanup callback, and specificdata key.
- `struct fileassoc_file` records a file handle, specificdata reference, association count, and hash-chain linkage.
- `struct fileassoc_table` stores the per-mount hash table, mask, slot counts, and table specificdata.
- `fileassoc_global` tracks global association use count and an `inuse` flag so vnode fast paths can skip work without global locking when fileassoc is unused.

Initialization and registration:
- `fileassoc_init()` creates the mount-specific key with `table_dtor()` and initializes the specificdata domain and global lock.
- `fileassoc_register()` runs initialization once, creates a specificdata key, allocates a `fileassoc`, inserts it in the global list, and returns the handle.
- `fileassoc_deregister()` removes the association, deletes its key, and frees the descriptor.

Lookup, table, and file entry handling:
- `fileassoc_table_lookup()` first checks the relaxed global `inuse` flag, runs lazy initialization if needed, and fetches the table from mount-specific storage.
- `fileassoc_file_lookup()` composes or accepts a vnode file handle, hashes it, and compares fileid length/content to find an entry.
- `fileassoc_table_add()` creates the initial per-mount table and stores it in mount-specific data.
- `fileassoc_table_resize()` doubles table slots, rehashes existing file entries, checks consistency, and replaces the old hash/specificdata storage.
- `fileassoc_table_delete()` clears the mount-specific pointer and destroys the table with all entries.
- `file_free()` removes one file entry, runs cleanup for all registered associations, decrements global use counts, frees the file handle and specificdata, and releases memory.

Public operations:
- `fileassoc_lookup()` returns data for a vnode/association pair.
- `fileassoc_add()` creates a file entry if absent, rejects duplicate data with `EEXIST`, increments global use, stores the data, and increments the per-file association count.
- `fileassoc_clear()` runs the cleanup callback, clears association data, decrements the per-file association count, and decrements global use.
- `fileassoc_file_delete()` removes all association data for a vnode, using the kernel lock around lookup/free and then decrementing table usage.
- `fileassoc_table_run()` iterates over all file entries in a mount table and invokes a callback for non-null data for one association.
- `fileassoc_table_clear()` clears one association across a mount table.

Concurrency and integration:
- Mount-specific storage owns table lifetime through `table_dtor()`.
- `fileassoc_incuse()` uses `xc_barrier()` when transitioning from unused to used so relaxed readers see the enabled state before fast paths rely on it.
- Some operations rely on higher-level serialization or the big kernel lock; the file contains explicit comments that resizing needs to ensure no concurrent fileassoc users.

Risks and notes:
- `fileassoc_table_resize()` has an explicit concurrency warning: it needs assurance that nothing uses fileassoc during rehash.
- `fileassoc_table_clear()` comments that it may be missing `faf->faf_nassocs--`, so association counts can become stale for table-wide clears.
- File entries are not garbage-collected when their per-file association count drops to zero, except through explicit file/table deletion.
