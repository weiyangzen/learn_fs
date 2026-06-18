# File Research: sources/local-fs/ocfs2-tools/tunefs.ocfs2/op_list_sparse_files.c

## Role

Implements `--list-sparse`, a reporting operation that recursively scans regular files and reports files containing sparse holes. It also summarizes total hole clusters and free clusters.

## Data Structures

- `struct multi_link_file`: red-black-tree node keyed by inode block number, used to avoid double-counting hard-linked files.
- `struct list_ctxt`: traversal state including current path, inode, accumulated hole length, duplicate flag, callback pointer, and hard-link tree.

## Scan Flow

`list_sparse()` scans from the root directory, then scans each per-slot orphan directory. For each directory entry, `list_sparse_func()` reads the inode and recurses into directories or calls `list_sparse_file()` for regular files.

`iterate_file()` uses `ocfs2_get_clusters()` over the file's virtual cluster range. When `p_cluster` is zero, it treats the range as a hole and invokes the supplied callback. It also supports callbacks for unwritten extents and extents beyond `i_size`, though this operation only uses the hole callback.

`list_sparse_file()` skips inline-data files, uses the hard-link tree for files with `i_links_count > 1`, and prints inode number, hole cluster count, and path when holes are present.

`get_total_free_clusters()` reads the global bitmap inode and computes `i_total - i_used`.

## Output

The operation prints tabular lines:

- inode block number
- cluster count for holes
- filepath

It also prints per-root/per-orphan-dir totals, total hole clusters in the volume, and total free clusters from the global bitmap.

## Open Flags

Declared as `TUNEFS_FLAG_RW`, even though the implementation is read/report oriented. This may be because directory iteration or library open semantics require stronger locking.

## Notable Risks

- `list_sparse_func()` allocates `di_buf`, then returns immediately for non-directory/non-regular files without freeing it. That is a memory leak during traversal.
- The path buffer is `OCFS2_MAX_FILENAME_LEN`, but the length guard compares against `PATH_MAX`. If `PATH_MAX` is larger, path construction can overflow the smaller buffer.
- Recursion is depth-first through directories with a fixed path buffer; extremely deep trees are not robustly handled.
