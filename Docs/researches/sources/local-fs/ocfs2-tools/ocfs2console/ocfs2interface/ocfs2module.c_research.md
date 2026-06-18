# File Research: sources/local-fs/ocfs2-tools/ocfs2console/ocfs2interface/ocfs2module.c

Python 2 C extension binding read-oriented `libocfs2` filesystem access for the GUI.

Exposed module:
- `ocfs2`

Exposed types:
- `ocfs2.Filesystem`
  - Opens an OCFS2 device, default flags `OCFS2_FLAG_RO | OCFS2_FLAG_BUFFERED`.
  - Read-only properties for fs sizing, roots, superblocks, UUID string.
  - Methods:
    - `flush`
    - `clusters_to_blocks`
    - `blocks_to_clusters`
    - `blocks_in_bytes`
    - `clusters_in_blocks`
    - `block_out_of_range`
    - `lookup_system_inode`
    - `read_cached_inode`
    - `dir_iterate`
    - `iterdir`
- `ocfs2.SuperBlock`
  - Exposes revision, mount/error state, features, block/cluster bits, max slots, label, UUID, root/system block numbers.
- `ocfs2.DInode`
  - Exposes inode metadata: size, timestamps, block number, flags, mode, uid/gid, links, clusters, bitmap totals, etc.
- `ocfs2.DirEntry`
  - Exposes name, inode, record length, file type.
- `ocfs2.DirScanIter`
  - Python iterator over directory entries.

Key implementation details:
- Opens devices with `ocfs2_open`.
- Closes with `ocfs2_close`.
- Reads cached inodes with `ocfs2_read_cached_inode`.
- Directory scanning uses:
  - `ocfs2_dir_iterate` for callback style
  - `ocfs2_open_dir_scan` / `ocfs2_get_next_dir_entry` for iterator style
- Creates `ocfs2.error` exception.

Exposed constants:
- OCFS2 block/cluster sizing, signatures, flags, feature/system inode constants, directory entry constants, file type constants, and max lengths.

Notable issues:
- `fs_blocks_to_clusters()` calls `ocfs2_clusters_to_blocks(self->fs, blocks)` instead of a blocks-to-clusters helper, which appears semantically wrong.
- `fs_dir_iterate()` ignores `ret` from `ocfs2_dir_iterate` and always returns `None`; callback exceptions are also not propagated robustly.
- `DirEntry` keeps `fs_obj` pointer but its deallocator does not `Py_DECREF(self->fs_obj)`, unlike `DInode` and `SuperBlock`.
