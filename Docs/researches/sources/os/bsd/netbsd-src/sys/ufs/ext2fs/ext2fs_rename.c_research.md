# File Research: sources/os/bsd/netbsd-src/sys/ufs/ext2fs/ext2fs_rename.c

This file adapts ext2fs rename to NetBSD's `genfs_sane_rename` framework. It supplies ext2fs-specific checks, directory-entry mutation, link-count manipulation, `..` rewriting, genealogy walking, and lookup-result recalculation.

Key responsibilities:
- Wrap old VOP rename API with `genfs_insane_rename`.
- Implement `genfs_rename_ops` callbacks for ext2fs.
- Enforce immutable/append flags and credential checks using UFS-like genfs helpers.
- Move directory entries, replace targets, and adjust source/target/parent link counts.
- Prevent invalid directory ancestry moves by walking `..`.
- Recalculate source lookup results if insertion compaction moved the source entry.

Important functions:
- `ext2fs_sane_rename`: Calls `genfs_sane_rename` with ext2fs rename operations and ext2fs lookup-result storage.
- `ext2fs_rename`: VOP entry point, immediately delegates to `genfs_insane_rename`.
- `ext2fs_gro_directory_empty_p`: Uses `ext2fs_dirempty`.
- `ext2fs_gro_rename_check_possible`: Uses `genfs_ufslike_rename_check_possible` with ext2 `EXT2_IMMUTABLE` and `EXT2_APPEND` flags.
- `ext2fs_gro_rename_check_permitted`: Delegates sticky/ownership/permission checks to `genfs_ufslike_rename_check_permitted`.
- `ext2fs_gro_remove_check_possible` and `ext2fs_gro_remove_check_permitted`: Equivalent checks for remove-via-rename cases.
- `ext2fs_gro_rename`: Main mutation routine. It temporarily increments source link count, creates or rewrites the target entry, updates target link counts, rewrites `..` when reparenting a directory, recalculates overlapping lookup results if needed, then removes the source entry and decrements the temporary source link.
- `ext2fs_rename_ulr_overlap_p`: Detects when target insertion compaction can affect the recorded source deletion slot.
- `ext2fs_rename_recalculate_fulr`: Re-scans the affected range to find the moved source entry and recompute `ulr_offset`, `ulr_reclen`, and preceding-entry length.
- `ext2fs_gro_remove`: Removes a non-directory link and decrements link count.
- `ext2fs_gro_lookup`: Calls `relookup`, unlocks the returned vnode, and copies `dvp->i_crap`.
- `ext2fs_gro_genealogy`: Locks and climbs from target directory via `..` to determine whether source is an ancestor.
- `ext2fs_read_dotdot`: Reads the directory template at offset zero and validates the `..` entry.
- `ext2fs_rename_replace_dotdot`: Decrements old parent link count and rewrites the child directory's `..` entry to the new parent.
- `ext2fs_gro_lock_directory`: Locks a directory and fails if it appears rmdir'd.

Important interactions:
- Depends heavily on `ext2fs_direnter`, `ext2fs_dirrewrite`, `ext2fs_dirremove`, `ext2fs_dirempty`, `ext2fs_update`, and `ext2fs_truncate`.
- Uses the same `i_crap` lookup result mechanism as create/remove/link/mkdir paths.
- The `ext2fs_genfs_rename_ops` table wires ext2fs into genfs rename sequencing.

Notable behavior and risks:
- Many comments mark unresolved recovery questions, especially around partial failure after link-count or directory-entry changes.
- `ext2fs_rename_replace_dotdot` writes the updated `..` entry but ignores the write error.
- Some cache purge calls are explicitly questioned in comments and are not consistently applied.
- `ext2fs_rmdired_p` defines removed directories as size zero, with a comment questioning correctness.
