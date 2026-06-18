# File Research: sources/local-fs/erofs-utils/lib/rebuild.c

This file builds/merges an in-memory target tree from existing EROFS filesystems, container layer paths, and incremental base directories.

Path/dentry construction:
- `erofs_rebuild_mkdir()` creates implicit parent directories with inherited uid/gid/mtime and parent-derived write bits.
- `erofs_d_lookup()` searches a directory’s child dentries by name.
- `erofs_rebuild_get_dentry()` walks a writable path string, creates missing intermediate directories, supports `..`, optionally recognizes AUFS whiteouts (`.wh.` prefix) and opaque directory markers, and optionally moves found dentries to list head.

Data conversion:
- `erofs_rebuild_write_blob_index()` converts supported source file mappings into chunk indexes for the target filesystem, creating unhashed blob chunks from mapped physical addresses.
- `erofs_rebuild_update_inode()` normalizes source inodes for the target: encodes device numbers, reads symlink content into memory, marks whiteout parents, and chooses blob-index or reserved-space handling for regular files.

Tree merge:
- `erofs_rebuild_dirent_iter()` is the callback for source-tree traversal. It merges lower-layer directory entries, skips entries shadowed by upper layers or opaque directories, preserves hard links for regular files, reads xattrs, updates source inode data mode, and recursively descends into directories.
- `erofs_rebuild_load_tree()` reads a source superblock/root inode and iterates it into a target root with a selected data mode.

Incremental base:
- `erofs_rebuild_basedir_dirent_iter()` records base directory entries as already-valid NIDs or updates existing in-memory child directory identity for recursive loading.
- `erofs_rebuild_load_basedir()` loads entries from an existing target/base directory into a current in-memory directory and inherits root xattr size.

Overlay/container semantics:
- AUFS whiteouts and opaque directories are understood by `erofs_rebuild_get_dentry()`.
- EROFS whiteouts are detected with `erofs_inode_is_whiteout()` / `erofs_dentry_is_wht()` in inode code.

Important dependencies:
- `erofs_iterate_dir`, `erofs_read_inode_from_disk`, `erofs_read_xattrs_from_disk`, `erofs_map_blocks`, blobchunk helpers, UUID helpers.

Risks / notes:
- `EROFS_REBUILD_DATA_FULL` is declared but regular file handling returns `-EOPNOTSUPP` unless blob-index or reserved-space mode is selected.
- `erofs_rebuild_get_dentry()` mutates path separators while walking, so callers must not pass string literals.
