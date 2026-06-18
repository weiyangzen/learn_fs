# File Research: sources/os/bsd/netbsd-src/sys/ufs/ufs/ufs_rename.c

This file adapts UFS rename to NetBSD’s `genfs_sane_rename` framework. It supplies UFS-specific checks, directory entry mutations, ancestry walking, and lookup-result management.

Key responsibilities:
- Wrap old VOP rename arguments with the saner genfs rename API.
- Enforce UFS immutable/append constraints and credential checks.
- Move entries between directories, replace targets, or remove duplicate links.
- Adjust link counts for files, directories, old parents, and new parents.
- Rewrite `..` when a directory is reparented.
- Recalculate source lookup results when target insertion compacts the same directory block.
- Detect invalid ancestry moves by walking parent links.

Important functions:
- `ufs_sane_rename`: Calls `genfs_sane_rename` with UFS lookup-result storage.
- `ufs_rename`: VOP entry point through `genfs_insane_rename`.
- `ufs_gro_directory_empty_p`: Uses `ufs_dirempty`.
- `ufs_gro_rename_check_possible` / `ufs_gro_rename_check_permitted`: Delegate UFS-like flag and credential checks to genfs helpers.
- `ufs_gro_rename`: Performs the rename under WAPBL: temporary source link bump, target creation or rewrite, target cleanup, `..` rewrite for reparented directories, source lookup-result recalculation, and source removal.
- `ufs_rename_ulr_overlap_p`: Detects whether a target insertion slot overlaps the source lookup region.
- `ufs_rename_recalculate_fulr`: Rescans the affected directory block to recover the source offset and previous record length after compaction.
- `ufs_gro_remove`: Handles rename-over-self as a remove of one link.
- `ufs_gro_lookup`: Performs `relookup`, unlocks the found vnode, and copies `i_crap`.
- `ufs_gro_genealogy`: Walks `..` from target directory toward root to detect whether the source parent is an ancestor.
- `ufs_read_dotdot`: Reads and validates the `..` entry.
- `ufs_gro_lock_directory`: Locks a directory and fails if it appears already removed.

Important interactions:
- Uses `ufs_direnter`, `ufs_dirrewrite`, `ufs_dirremove`, `ufs_dirempty`, `ufs_blkatoff`, `ufs_bufio`, `vcache_get`, and WAPBL.
- The `genfs_rename_ops` table at the end wires all callbacks into the generic rename engine.

Notable behavior and risks:
- Comments explicitly call out fragile historical link-count asymmetries and incomplete rollback questions.
- Some error branches that might back out changes are disabled with `#if 0`.
- Removed directories are detected by zero size, with a comment questioning whether that is fully correct.
