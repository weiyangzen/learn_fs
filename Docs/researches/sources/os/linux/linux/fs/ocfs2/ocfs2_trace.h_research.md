# File Research: sources/os/linux/linux/fs/ocfs2/ocfs2_trace.h

Role: Defines the OCFS2 ftrace tracepoint catalogue. It sets `TRACE_SYSTEM ocfs2`, declares reusable event classes, instantiates trace events for most OCFS2 subsystems, and ends with `TRACE_INCLUDE_PATH`, `TRACE_INCLUDE_FILE`, and `<trace/define_trace.h>`.

Reusable event classes:
- Single-value classes for `int`, `unsigned int`, `unsigned long long`, pointer, and string.
- Multi-value numeric classes for common combinations of ints, uints, and 64-bit values.
- Specialized classes for B-tree operations, truncate-log operations, refcount tree records, get-block calls, file operations, xattr lookup, and dentry operations.
- Macros such as `DEFINE_OCFS2_INT_EVENT()` and `DEFINE_OCFS2_ULL_UINT_EVENT()` reduce boilerplate for simple tracepoints.

Subsystem trace coverage:
- `alloc.c`: extent B-tree insertion, split, rotation, truncate commit, extent validation, unwritten extents, trim/discard, and allocation tree changes.
- `truncate_log.c`/deallocation paths: truncate-log append/replay/flush, recovery, cached cluster/block frees, and dealloc runs.
- `localalloc.c`: local allocation sizing, selection, bitmap scanning, sync back to main allocator, and new allocation windows.
- `resize.c`: group extension and group addition.
- `suballoc.c`: group descriptor validation, block group allocation, suballocator reservation/claim/free, chain search, and inode bit tests.
- `refcounttree.c`: refcount block validation, refcount tree creation/purge, record insertion/splitting, refcount increase/decrease, metadata credit calculation, COW cluster replacement, and making clusters writable.
- `aops.c`: `get_block`, symlink block mapping, readpage/bmap, inline write attempts, write begin, and inline write completion.
- `mmap.c`: page fault tracing.
- `file.c`: open/release/sync/read/write/splice, truncate, allocation extension, zeroing, setattr, suid removal, partial-cluster zeroing, range removal, and write preparation.
- `inode.c`: iget lifecycle, inode population, orphan recovery state checks, inode block validation/filecheck repair, delete/wipe decisions, revalidation, and dirty marking.
- `extent_map.c`: virtual block reads.
- `slot_map.c`: slot info refresh, slot buffer mapping, and slot selection.
- `heartbeat.c`: node-down handling.
- `super.c`: remount, fill_super, option parsing, put_super, statfs, dismount, and super initialization.
- `xattr.c`: xattr block validation, allocation extension, xattr set context, bucket/index lookup, bucket movement/splitting/defrag, indexed xattr growth, xattr truncation, reflinked xattrs, and empty xattr block creation.
- `reservations.c`: reservation insertion, free-bit search, window finding, reservation cannibalization, and claimed-bit updates.
- `quota_local.c` and `quota_global.c`: local quota recovery, dquot sync, read/write/acquire/release, quota block validation, and dirty dquot marking.
- `dir.c`: directory block search/validation, indexed directory lookup, entry checks, dx root formatting, directory extension, rebalance, and insert preparation.
- `namei.c`: lookup/create/mkdir/unlink/symlink/move-orphan dentry events, mknod, hard link, unlink no-entry races, double locks, rename, rename denial/target races, symlink data, orphan-name formatting, orphan add/delete.
- `dcache.c`: dentry revalidation, negative dentry generation checks, orphan/delete/nofsdata cases, dentry lock attachment.
- `export.c`: NFS export dentry lookup, stale/generation checks, parent lookup, and file-handle encoding.
- `journal.c`: cache commits, transaction extension, journal access/dirty/init/shutdown, recovery completion, recovery thread/node handling, journal replay, orphan recovery queueing, orphan filldir, orphan recovery, and mount waits.
- `buffer_head_io.c`: synchronous and async block reads/writes.
- `uptodate.c`: metadata cache purge, buffer cache lookup, cache array/tree insertions, expansion, uptodate marking, and cache removal.

Namei-relevant details:
- The dentry event class records directory pointer, dentry pointer, name length/name, parent block number, and an extra value.
- Rename tracepoints capture old/new directories and names plus special target-exists/disagreement/overwrite cases.
- Orphan tracepoints record add begin/end, delete directory/name, and block-number stringification.
- Double-lock tracepoints record the two inode block numbers before and after lock ordering.

Design notes:
- The header is declarative but central to OCFS2 observability; adding/removing function instrumentation often requires updates here.
- Tracepoints avoid heavyweight formatting in hot paths by using ftrace `TP_fast_assign` and `TP_printk`.
