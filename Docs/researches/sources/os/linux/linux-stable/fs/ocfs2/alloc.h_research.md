# File Research: sources/os/linux/linux-stable/fs/ocfs2/alloc.h

Purpose: declares OCFS2 allocation and extent-tree APIs, public extent-tree/path structures, delayed-deallocation context, truncate-log interfaces, inline-data conversion helpers, truncate helpers, and trim entry point.

Read coverage: complete file read, 308 lines.

Key structures and constants:
- `OCFS2_MAX_XATTR_TREE_LEAF_SIZE` caps xattr tree leaf payload at 64 KiB.
- `struct ocfs2_extent_tree` is the public context object for generic extent-tree manipulation. It carries operation callbacks, root buffer, root extent list, caching info, root journal-access function, backing object, max leaf cluster limit, and optional delayed-deallocation context.
- `enum ocfs2_alloc_restarted` tells allocation callers why `ocfs2_add_clusters_in_btree()` returned `-EAGAIN`: no restart, transaction restart, or metadata reservation restart.
- `struct ocfs2_cached_dealloc_ctxt` stores delayed suballocator frees and global cluster frees.
- `struct ocfs2_truncate_context` combines delayed deallocation state, extent allocator lock state, and the last extent-block buffer used by truncation setup.
- `struct ocfs2_path_item` and `struct ocfs2_path` model a bounded root-to-leaf extent b-tree path. `OCFS2_MAX_PATH_DEPTH` is 5.
- Path macros expose root/leaf buffer heads, root/leaf extent lists, root access function, and item count.

Declared behavior:
- Extent-tree initialization functions support dinode, xattr tree, xattr value, directory index root, and refcount tree roots.
- Extent block reading is cached and validated by the implementation before returning a buffer head.
- Extent mutation APIs cover insert, cluster allocation into a b-tree, split, mark-written, generic flag change, extent removal, and removal of a full b-tree range with optional refcount-tree locking.
- `ocfs2_extend_meta_needed()` conservatively returns maximum metadata blocks needed for tree growth: current depth plus two.
- Dinode layout helpers switch between inline data and extent-list formats and convert inline data into extents.
- Truncate-log APIs initialize/shutdown the per-slot log, schedule flush work, append records, flush synchronously, recover another slot’s truncate log, and check/try flush capacity.
- Delayed-deallocation APIs initialize contexts, cache cluster/block frees, test whether global cluster frees exist, and run cached deallocations.
- Truncate helpers zero partial ranges, commit extent truncation, and truncate inline data.
- Path helpers allocate/reuse/free paths, find paths/leaves/neighbor cpos values, journal path buffers, and identify subtree roots for rotations.
- `ocfs2_trim_fs()` is the exported fstrim entry point.

Inline helpers:
- `ocfs2_init_dealloc_ctxt()` zeroes delayed-deallocation list heads.
- `ocfs2_dealloc_has_cluster()` reports whether a delayed context contains pending global cluster frees.
- `ocfs2_rec_clusters()` reads cluster length from `e_int_clusters` for interior nodes and `e_leaf_clusters` for leaf nodes.
- `ocfs2_is_empty_extent()` treats a leaf record with zero `e_leaf_clusters` as empty.

Important dependencies:
- Requires OCFS2 on-disk structures such as `ocfs2_extent_list`, `ocfs2_extent_rec`, and `ocfs2_dinode`, plus OCFS2 caching and journal-access types.
- Exposes APIs that are consumed by file growth/truncate paths, xattr code, directory indexing, refcount-tree code, and trim/ioctl handling.

Concurrency and lifetime:
- Callers supply journal handles, allocator contexts, buffer heads, and path objects; the header makes the split ownership model explicit but leaves locking rules to higher-level OCFS2 code.
- Prepared paths own buffer-head references until `ocfs2_reinit_path()` or `ocfs2_free_path()`.
- Delayed-deallocation contexts must be initialized before use and drained after mutating operations complete with no active journal handle.
- Truncate-log functions require the implementation’s lock ordering around the truncate-log inode and global bitmap inode.

Risk and edge cases:
- `ocfs2_extend_meta_needed()` is intentionally conservative; callers may reserve more metadata than a specific operation ultimately consumes.
- `ocfs2_rec_clusters()` must be used with the correct node depth or callers will read the wrong union field.
- Empty extents are only meaningful for leaf records; using `ocfs2_is_empty_extent()` on interior records would be semantically wrong.
- Path depth is fixed by `OCFS2_MAX_PATH_DEPTH`; corrupt on-disk depths beyond that are rejected by implementation checks.
- Mutation APIs require matching metadata reservations and delayed-deallocation handling from callers, especially for split, truncate, and refcounted-removal paths.
