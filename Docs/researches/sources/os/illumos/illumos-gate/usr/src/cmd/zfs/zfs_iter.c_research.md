# File Research: sources/os/illumos/illumos-gate/usr/src/cmd/zfs/zfs_iter.c

This file implements the private dataset iteration engine used by `zfs list`, `zfs get`, `zfs inherit`, `zfs upgrade`, key management, holds, and other subcommands.

Main API:
- `zfs_for_each(argc, argv, flags, types, sortcol, proplist, limit, callback, data)`: opens requested datasets, recursively gathers matching descendants when requested, stores handles in a sorted AVL tree, invokes the caller callback in sorted order, then closes all retained handles.
- `zfs_add_sort_column(sc, name, reverse)`: appends a native or user-property sort key.
- `zfs_free_sort_columns(sc)`: releases the sort list.
- `zfs_sort_only_by_name(sc)`: detects the simple `name`-only sort case.

Iteration behavior:
- With no dataset arguments, it iterates all roots via `zfs_iter_root()` and forces recursive traversal.
- With explicit arguments, it opens by dataset name or path depending on `ZFS_ITER_ARGS_CAN_BE_PATHS`.
- Recursive mode always permits filesystems as traversal roots; if snapshots or bookmarks are requested, volumes can also be traversal roots.
- Filesystems recurse through child filesystems.
- Snapshots are included when the requested type includes snapshots, or when `ZFS_ITER_PROP_LISTSNAPS` is active and the pool `listsnapshots` property is set.
- Bookmarks are included when the requested type includes bookmarks.
- `ZFS_ITER_DEPTH_LIMIT` bounds recursion by `cb_depth_limit`.
- `ZFS_ITER_SIMPLE` selects the simple snapshot iterator for fast name-only listing.

Sorting behavior:
- Dataset handles are retained in a libuutil AVL tree.
- Explicit sort columns can be native numeric properties, native string properties, `name`, or user properties.
- Invalid-for-row properties sort that row to the bottom.
- Reverse sorting is handled per column.
- If explicit columns tie or no columns are given, `zfs_compare()` sorts by dataset name with snapshots grouped under parents and snapshots ordered by `createtxg` when available.
- `zfs_compare()` temporarily truncates names at `@` while comparing parent names, then restores the delimiters before returning.

Property handling:
- When a property list is supplied, the iterator can prune handles down to only properties needed by the output list and sort columns.
- It always preserves `zoned` and `createtxg` when pruning, because other property paths and snapshot ordering depend on them.
- It expands property lists with received or literal formatting when `ZFS_ITER_RECVD_PROPS` or `ZFS_ITER_LITERAL_PROPS` is set.

State and ownership:
- Nodes own retained `zfs_handle_t *` values only after successful insertion into the AVL tree.
- Duplicate handles are closed immediately.
- The final robust AVL walk removes every node, closes each retained handle, and frees each node.
- `avl_pool` is a file-scope global initialized per `zfs_for_each()` call.

Risk notes:
- Callback callers must not access properties pruned out of the handle unless they supplied them in the property or sort lists.
- The snapshot inclusion rule depends both on command flags and the pool `listsnapshots` property, so list/get behavior can differ when types are omitted.
- The global `avl_pool` makes the helper unsuitable for concurrent independent invocations inside one process.
- The comparator mutates handle name buffers in place around `@`; correctness depends on restoring those bytes on every path.
