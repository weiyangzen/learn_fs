# File Research: sources/os/bsd/netbsd-src/sys/ufs/ext2fs/ext2fs_lookup.c

This file implements ext2fs directory reading, lookup, directory-entry insertion/removal/rewrite, and empty-directory checks. It is adapted from UFS lookup code but accounts for ext2 on-disk directory formats, ext2 byte order helpers, optional directory entry file-type fields, and htree indexed directories.

Key responsibilities:
- Convert ext2 directory entries to NetBSD `struct dirent` records for `readdir`.
- Resolve path components using namecache, htree lookup when available, and linear directory scans.
- Produce and consume `struct ufs_lookup_results` stored in `inode.i_crap` for later create/delete/rename operations.
- Insert, compact, remove, and rewrite ext2 directory entries.
- Validate directory entries when `dirchk` is enabled.
- Check whether a directory contains only `.` and `..`.

Important functions:
- `ext2fs_dirconv2ffs`: Converts `struct ext2fs_direct` to `struct dirent`, including inode number conversion, name length, optional file type translation via `ext2dt2dt`, and `_DIRENT_SIZE` recomputation because ext2 and FFS directory record sizes differ.
- `ext2fs_readdir`: Reads raw directory bytes with `UFS_BUFRD`, walks ext2 records, converts one entry at a time, emits cookies, fixes `uio_offset` to raw ext2 offsets, and sets EOF based on inode size.
- `ext2fs_lookup`: Main VOP lookup. It checks execute permission, readonly mutation restrictions, namecache, exclusive directory locking, and directory slot accounting. It uses htree lookup for non-dot names on indexed directories and otherwise performs one- or two-pass linear scanning. On create/rename miss it records a usable insertion slot and returns `EJUSTRETURN`; on found entries it handles LOOKUP, DELETE, and RENAME cases with correct vnode lookup and sticky-directory authorization.
- `ext2fs_search_dirblock`: Shared scanning helper used by htree code. It performs forward-progress validation, optional free-slot accumulation, and exact name matching inside a directory block.
- `ext2fs_dirbadentry`: Validates record length, alignment, name length, block containment, and inode range. It currently prints and panics on bad entries when invoked.
- `ext2fs_direnter`: Builds a new ext2 directory entry, including optional `EXT2F_INCOMPAT_FTYPE` type field. For htree directories it delegates to `ext2fs_htree_add_entry` and clears `EXT2_INDEX` if insertion fails. For linear directories it either appends a fresh block or calls `ext2fs_add_entry`.
- `ext2fs_add_entry`: Compacts a free range discovered by lookup and writes a new directory entry into the resulting free space.
- `ext2fs_dirremove`: Removes an entry by zeroing its inode if first in block, or merging its record length into the previous entry.
- `ext2fs_dirrewrite`: Repoints an existing directory entry to a different inode and updates the optional type byte.
- `ext2fs_dirempty`: Reads minimal directory-entry headers and accepts only `.` plus `..` pointing to the expected parent.

Important interactions:
- Depends on `ext2fs_blkatoff`, `ext2fs_bufwr`, `ext2fs_truncate`, htree helpers, UFS namecache helpers, and UFS vnode/inode infrastructure.
- `ext2fs_lookup` stores mutation metadata in `dp->i_crap` and increments `i_crapcounter`; consumers in `ext2fs_vnops.c` and `ext2fs_rename.c` validate this with UFS macros.
- Directory insertion can truncate unused tail space based on `ulr_endoff`.

Notable behavior and risks:
- Lookup may return `ENOLCK` if the directory is not exclusively locked after a namecache miss, implying upper VFS code must retry with stronger locking.
- `ext2fs_dirbadentry` panics after setting `error_msg`, making `return error_msg == NULL ? 0 : 1` effectively unreachable on invalid entries.
- `ext2fs_readdir` allocates a full read buffer plus one `dirent`, converts entry by entry, and avoids partial returned `dirent` records.
- The htree insert path clears the inode's `EXT2_INDEX` flag on failure but returns the original error.
