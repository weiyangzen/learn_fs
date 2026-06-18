# File Research: sources/os/linux/linux/fs/xfs/scrub/nlinks.c

## Role
Implements live filesystem-wide inode link-count scrub for XFS. Link counts are treated as summary metadata derived from directory entries and parent pointers, so this file builds a shadow counter table by scanning all inodes and then compares it against actual inode `i_nlink` values.

## Setup
- `xchk_setup_nlinks` enables the dirent fsgate, prepares repair via `xrep_setup_nlinks` when possible, allocates `struct xchk_nlink_ctrs`, and calls `xchk_setup_fs`.
- `xchk_nlinks_setup_scan` initializes the collection iscan, creates a sparse `xfarray` large enough for possible inode numbers, installs a directory update hook, and arranges deferred cleanup.

## Collection Phase
- `xchk_nlinks_collect` first counts superblock-rooted metadata files, then walks all allocated inodes.
- Directories are locked with IOLOCK plus ILOCK, scanned through `xchk_dir_walk`, and optionally scanned for parent-pointer xattrs.
- Non-directories simply advance the iscan cursor under IOLOCK.
- Temporary repair staging files/directories are ignored to avoid counting repair internals.

## Counters
- `xchk_nlinks_update_incore` updates `parents`, `backrefs`, and `children` in the sparse `xfarray`.
- `careful_add` clamps counters to `U32_MAX`; later checks still catch values beyond XFS limits.
- Directory entries increment parent counts for children and child counts for directories; `..` contributes backrefs unless parent pointers are enabled.

## Live Updates
- `xchk_nlinks_live_update` receives dirent notifications while the scan is running.
- Updates are applied only when the affected inode or directory has already been scanned.
- Hook failures abort the iscan, forcing `INCOMPLETE` so repair cannot use partial data.

## Comparison Phase
- `xchk_nlinks_compare` walks all allocated inodes and compares actual link counts to observed totals.
- Skipped or leftover observations are checked with `xchk_nlinks_compare_inum`, using AGI protection for missing/unallocated inode numbers.
- Directories require matching child/backref counts; non-directories and unlinked directories must not have backrefs or children.
- Overflow beyond `XFS_NLINK_PINNED` is corruption; values beyond `XFS_MAXLINK` are warnings.

## Risk Points
- Correctness depends on live dirent hooks staying installed until repair or teardown.
- Any collection error must set `INCOMPLETE`; otherwise repair could write bad link counts.
- Parent-pointer filesystems derive directory backrefs from xattrs instead of `..` entries.
