# File Research: sources/os/bsd/freebsd-src/sys/ufs/ufs/ufs_lookup.c

## Purpose
Implements UFS directory lookup and directory-entry manipulation. This is the core bridge between namei/pathname resolution and on-disk UFS directory blocks.

## Key entry points
- `ufs_lookup()` is the `VOP_CACHEDLOOKUP` wrapper around `ufs_lookup_ino()`.
- `ufs_lookup_ino()` searches a directory for a component, optionally returning a vnode or just an inode number. It also records mutation state in directory inode fields for later create, delete, rename, and whiteout operations.
- `ufs_makedirentry()` builds a `struct direct` from an inode and component name, handling old UFS directory format quirks.
- `ufs_direnter()` inserts a new directory entry, either by allocating a new directory block or compacting/reusing free space in an existing block.
- `ufs_dirremove()` removes or whiteouts a directory entry and adjusts link counts, softdep state, dirhash state, and disclosure-sensitive name metadata.
- `ufs_dirrewrite()` changes an existing directory entry to point to a new inode, used heavily by rename.
- `ufs_dirempty()` verifies a directory contains only valid `.` and `..` entries, optionally ignoring whiteouts.
- `ufs_checkpath()` walks `..` links to prevent directory renames from creating cycles.
- Diagnostic tracker functions validate ownership of `i_offset`, `i_count`, and `i_endoff` when `DIAGNOSTIC` is enabled.

## Lookup algorithm
The lookup path uses the name cache through `vfs_cache_lookup()` and falls back here for cache misses. It:
- Verifies the directory is still linked via `i_effnlink`.
- Creates a VM object for directory VMIO when needed.
- Uses `ufsdirhash` opportunistically for large directories.
- Otherwise scans directory blocks linearly, optionally starting from cached `i_diroff` for ordinary lookups.
- Tracks reusable slots for create/rename by recording `i_offset`, `i_count`, and `i_endoff`.
- Handles whiteouts by treating matching `DT_WHT` entries as create/delete not-found cases with `ISWHITEOUT`.
- Handles `DELETE`, `RENAME`, `CREATE`, ordinary lookup, `.`, and `..` as distinct cases.

## Directory mutation behavior
- `ufs_direnter()` can grow the directory by one `DIRBLKSIZ` block or compact an existing region. It updates dirhash, softdep dependencies, inode size, VM pager size, and write ordering.
- `ufs_dirremove()` decrements `i_effnlink` first so softdep can block, then updates on-disk link count immediately for non-softdep filesystems. Removed entry names are zeroed to reduce disk scavenging disclosure.
- `ufs_dirrewrite()` protects against stale `..` rewrites by checking that a `..` entry still references the expected old inode, returning `EIDRM` if it changed.

## Access and safety checks
- `ufs_delete_denied()` combines optional NFSv4 ACL delete semantics with traditional Unix write permission and sticky-directory ownership rules.
- `ufs_dirbadentry()` validates record length, block fit, minimum entry size, name length, and null termination when directory checking is enabled.
- `ufs_checkpath()` uses cached parent vnode information when available, falls back to reading `..`, and reports a wait inode if nonblocking `VFS_VGET` would block.

## Dependencies
Uses `UFS_BLKATOFF`, `UFS_BALLOC`, `UFS_UPDATE`, dirhash functions, softdep directory hooks, quota setup for directory growth, vnode/namecache APIs, and FFS-facing helpers.

## Research notes
This file is stateful by design: name lookup prepares precise directory insertion/removal offsets consumed later by vnode operations. Correct locking is central, especially for mutation lookups where the parent directory must remain exclusively locked so `i_offset/i_count/i_endoff` remain valid.
