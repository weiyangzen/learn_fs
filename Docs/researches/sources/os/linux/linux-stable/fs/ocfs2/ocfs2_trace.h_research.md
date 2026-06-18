# File Research: sources/os/linux/linux-stable/fs/ocfs2/ocfs2_trace.h

Purpose: declares the OCFS2 ftrace tracepoint surface for allocation, local allocation, resize, suballocation, refcount/COW, address-space operations, mmap, file operations, inode lifecycle, extent maps, slot maps, heartbeat, superblock operations, xattrs, reservations, quotas, directory operations, namespace operations, dcache, export/NFS file handles, journaling/recovery, buffer-head I/O, and metadata-cache tracking.

Read coverage: complete file read, 2,764 lines.

Tracepoint infrastructure:
- Sets `TRACE_SYSTEM` to `ocfs2` and includes `<linux/tracepoint.h>`.
- Defines reusable event classes for common payload shapes: int, uint, ull, pointer, string, pairs/triples/quads of integers and block numbers, btree operations, truncate-log operations, refcount records, get-block events, file operations, xattr lookup events, and dentry operations.
- Ends with `TRACE_INCLUDE_PATH .`, `TRACE_INCLUDE_FILE ocfs2_trace`, and `<trace/define_trace.h>` outside the include guard as required by Linux tracepoint headers.

Subsystem coverage:
- Allocation and truncate-log events cover btree rotations/splits/inserts/removals, extent writes/truncates, trim/discard, cached deallocation, local allocation windowing, resize group add/extend, suballocator group allocation/search/claim/free, and group descriptor validation.
- Refcount events cover refcount block validation, tree creation/purge, record insert/split/increase/decrease, metadata credit calculation, COW duplication, refcount flag changes, cluster replacement, and writable-cluster conversion.
- AOP/file/mmap events cover block mapping, inline writes, write begin/end, page faults, file open/release/read/write/splice/fsync, truncation, allocation extension, zeroing, setattr, SUID removal, partial cluster zeroing, inode write preparation, and read/splice return values.
- Inode events cover iget, actor matching, inode population/read/validation/filecheck repair, orphan recovery state checks, delete/wipe queries, cleanup, clear, revalidation, and dirty marking.
- Super/recovery events cover remount, fill_super, option parsing, put_super, statfs, dismount, super initialization, journal commit/access/dirty/init/shutdown, recovery slots, recovery thread, journal replay, dead node marking, orphan scan/recovery, and mount waits.
- Directory/name/dcache/export events cover directory block validation/search, indexed directory searches/rebalances, lookup/create/mkdir/unlink/symlink/mknod/link/rename, orphan add/delete, dentry revalidation/attach, NFS dentry lookup, parent lookup, and file handle encoding.
- Xattr, reservation, quota, extent-map, slot-map, heartbeat, buffer I/O, and uptodate-cache events expose their module-specific state transitions and parameters.

Dependencies:
- Tracepoint users in OCFS2 C files call the generated `trace_ocfs2_*` functions; event declarations must match call-site argument types.
- Uses Linux tracepoint macros, string assignment helpers, device major/minor extraction, and pointer/integer formatting.

Risk and edge cases:
- Tracepoint ABI is externally observable through ftrace/perf tooling; renaming events or changing field order/types can break diagnostics.
- Several tracepoints copy names with `__string()` / `__assign_str()` and print with explicit lengths; call sites must pass valid pointers for traced names.
- Pointer values and block numbers are intentionally exposed for debugging but can be sensitive in production traces.
- Event-class macro reuse reduces boilerplate but means signature changes affect many events at once.
