# File Research: sources/os/bsd/netbsd-src/sys/ufs/ufs/ufs_lookup.c

This file implements core UFS directory lookup and directory-entry mutation helpers. It is shared by UFS-family vnode operations for create, delete, link, mkdir, rename, whiteout, directory compaction, and empty-directory checks.

Key responsibilities:
- Resolve pathname components in UFS directories through namecache, optional `UFS_DIRHASH`, and linear scans.
- Record mutation metadata in `inode.i_crap` as `struct ufs_lookup_results`.
- Find reusable directory slots, compact directory blocks, grow directories, and optionally truncate trailing unused directory space.
- Insert, remove, and rewrite `struct direct` directory entries with byte-order and old/new directory format handling.
- Validate directory entries and report bad directory structure.
- Provide `ufs_blkatoff` for reading the buffer that contains a directory offset.

Important functions:
- `ufs_lookup`: Main VOP lookup path. It enforces execute permission, readonly restrictions for delete/rename, namecache lookup, exclusive-lock retry (`ENOLCK`), dirhash/linear search, whiteout handling, slot accounting, DELETE/RENAME/CREATE semantics, and namecache insertion.
- `slot_*` helpers: Track free space and determine whether insertion needs a fresh directory block or compaction.
- `ufs_can_delete`: Enforces write/delete-child access and sticky-directory rules.
- `ufs_dirbad` / `ufs_dirbadentry`: Report and validate bad entries, including record length, block containment, advertised name length, and NUL termination.
- `ufs_makedirentry`: Builds a new `struct direct` for a component name and inode.
- `ufs_direnter`: Dispatches insertion to `ufs_dirgrow` or `ufs_dircompact`.
- `ufs_dirremove`: Removes or whiteouts an entry and decrements the target inode link count.
- `ufs_dirrewrite`: Repoints an existing entry and decrements the old inode link count.
- `ufs_dirempty`: Accepts only empty slots, whiteouts, `.`, and `..` with the expected parent.
- `ufs_blkatoff`: Reads the filesystem block containing an offset, with optional modify marking and simple readahead.

Important interactions:
- Used directly by `ufs_vnops.c` and `ufs_rename.c`.
- Uses `UFS_BALLOC`, `UFS_TRUNCATE`, `UFS_UPDATE`, `UFS_WAPBL_UPDATE`, `ufsdirhash_*`, `cache_lookup`, `cache_enter`, and `vcache_get`.
- The lookup-result fields are validated by callers via `UFS_CHECK_CRAPCOUNTER`.

Notable behavior and risks:
- Namecache misses under a non-exclusive directory lock return `ENOLCK` so callers can retry with stronger locking.
- Directory mutation helpers have asymmetric link-count behavior: `ufs_direnter` does not increment target links, while `ufs_dirremove` and `ufs_dirrewrite` decrement old/removed inode links.
- Several comments document old API baggage: unused parameters, fragile `i_crap` storage, and limited recovery if buffer writes fail after link counts change.
