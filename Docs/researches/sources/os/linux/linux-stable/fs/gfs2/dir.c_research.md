# File Research: sources/os/linux/linux-stable/fs/gfs2/dir.c

## Purpose
Implements GFS2 directory storage, lookup, readdir, add/delete/move operations, stuffed-to-exhash conversion, extendible hashing, leaf splitting/chaining, hash table caching, and exhash deallocation.

## Key Interfaces
- Lookup/read: `gfs2_dir_search()`, `gfs2_dir_check()`, and `gfs2_dir_read()`.
- Mutation: `gfs2_dir_add()`, `gfs2_dir_del()`, and `gfs2_dir_mvino()`.
- Allocation/deallocation: `gfs2_diradd_alloc_required()`, `gfs2_dir_get_new_buffer()`, and `gfs2_dir_exhash_dealloc()`.
- Cache helper: `gfs2_dir_hash_inval()`.

## Control Flow And Behavior
Small directories are stuffed in the dinode. Larger directories convert to exhash: the directory file becomes a hash table of leaf block pointers, while dirents live in leaf blocks that may be shared by multiple hash-table entries. Full leaves are split when possible; otherwise the hash table is doubled up to `GFS2_DIR_MAX_DEPTH`, then overflow leaves are chained.

Directory scanning validates record lengths, alignment, block type, name lengths, and sentinel rules. Readdir gathers dirents into arrays, assigns cookies based on hash or local offset, sorts where needed to keep hash collisions stable, and emits entries via `dir_emit()`. Add operations reuse saved allocation probes when possible, initialize dirents, update leaf/directory entry counts and timestamps, and increment parent nlink for subdirectories. Delete merges dirent record space or marks the first entry as empty, updates counts/timestamps, and drops parent nlink for directories.

## Dependencies
Uses GFS2 bmap allocation, metadata I/O, transactions, resource groups, quota, hash helpers, buffer heads, sort/vmalloc allocation, and inode dirtying.

## Risks And Invariants
Dirent corruption triggers consistency warnings and `-EIO`. Hash cache size must equal inode size for exhash directories. Leaf split/double operations must invalidate hash cache. Exhash deallocation rewrites hash table entries to zero and can temporarily change the inode mode to regular file on final deallocation to avoid double-free after crash.
