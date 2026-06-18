# File Research: sources/os/bsd/netbsd-src/sys/ufs/lfs/lfs_rename.c

## Purpose

`lfs_rename.c` adapts NetBSD's genfs sane/insane rename framework to LFS and ULFS directory formats. It performs permission/possibility checks, directory genealogy analysis, directory-entry mutation, link-count updates, LFS directory-operation bookkeeping, and orphan handling for overwritten targets.

## Main Responsibilities

- Supplies `genfs_rename_ops` callbacks for directory-empty checks, immutable/append checks, sticky/permission checks, remove, lookup, genealogy, lock-directory, and rename.
- Uses `struct ulfs_lookup_results` captured from `relookup()` to mutate directory entries efficiently.
- Recalculates source lookup results when target insertion compacts the same directory block and invalidates the old removal location.
- Reads `..` entries and walks parent directories to detect ancestry relationships.
- Implements actual ULFS-style rename semantics in `ulfs_gro_rename()`.
- Wraps ULFS rename in LFS-specific dirop setup/teardown in `lfs_gro_rename()`.
- Rejects `.` and `..` renames in `lfs_sane_rename()` before delegating to `genfs_sane_rename()`.

## Rename Flow

`ulfs_gro_rename()` first increments the source link count as a crash-recovery safety measure and writes that update through `lfs_update(..., UPDATE_DIROP)`. If the target does not exist, it optionally increments the new parent link count for directory reparenting and creates a new directory entry with `ulfs_direnter()`. If the target exists, it rewrites the target entry to point to the source with `ulfs_dirrewrite()`, adjusts parent link counts for directory replacement, and truncates overwritten directories to zero.

When moving a directory across parents, it rewrites the source directory's `..` entry to point to the new parent. Finally it removes the original source entry with `ulfs_dirremove()`, recalculating `fulr` first if an earlier `ulfs_direnter()` overlapped and compacted the relevant directory block.

## LFS-Specific Bookkeeping

`lfs_gro_rename()` calls `lfs_set_dirop(tdvp, tvp)`, marks source and parent vnodes with `MARK_VNODE`, delegates to `ulfs_gro_rename()`, orphans overwritten targets whose link count reaches zero, unmarks all involved vnodes, calls `lfs_unset_dirop()`, and releases references held for the operation.

## Safety Notes

The code relies heavily on `KASSERT` invariants for locked vnodes, mount equality, vnode distinctness, and type checks. Several comments document inherited UFS/ULFS rename awkwardness around link-count side effects in `ulfs_dirremove()` and `ulfs_dirrewrite()`. Crash consistency is handled through temporary link-count increments and LFS dirop partial-segment marking rather than a traditional journal.
