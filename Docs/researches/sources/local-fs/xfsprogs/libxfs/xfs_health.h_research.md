# File Research: sources/local-fs/xfsprogs/libxfs/xfs_health.h

## Purpose
Defines in-core XFS metadata health state masks and public health helper prototypes. It provides the common vocabulary for scrub, repair, runtime corruption detection, geometry reporting, bulkstat reporting, and health monitor conversion.

## Main Contents
- Health model:
  - Each domain has `checked` and `sick` bitsets.
  - `checked && sick` means checked and needs repair.
  - `checked && !sick` means checked healthy.
  - `!checked && sick` means runtime evidence exists but no thorough check.
  - `!checked && !sick` means not examined since mount.
- Filesystem health flags:
  - Counters, user/group/project quota, quota check, nlinks, metadata directory tree, metadata path.
- Realtime group health flags:
  - Superblock, bitmap, summary, rmapbt, refcountbt.
- AG health flags:
  - Superblock, AGF, AGFL, AGI, bnobt, cntbt, inobt, finobt, rmapbt, refcntbt, bad inodes.
- Inode health flags:
  - Core, data/attr/cow bmaps, directory, xattrs, symlink, parent pointers, erased/zapped fork states, forget marker, directory tree.
- Mask groupings:
  - Primary, secondary, indirect, zapped, and all masks per domain.
- Mark/measure APIs:
  - Filesystem, group/AG/RTG, and inode mark sick/corrupt/healthy/measure functions.
  - Helpers for bmap, btree, dirattr, and da-args sickness marking.
- Query helpers:
  - `xfs_fs_has_sickness`, `xfs_group_has_sickness`, `xfs_inode_has_sickness`, and healthy checks.
- Reporting conversion:
  - Geometry and bulkstat health fill functions.
  - Health monitor mask conversion helpers.
- Error helper:
  - `xfs_metadata_is_sick(error)` recognizes `-EFSCORRUPTED` and `-EFSBADCRC`.

## Dependencies and Integration
- Consumed by inode allocation and btree verifier paths to mark AGI/inobt/finobt sickness on corruption.
- Exported masks map onto userspace ABI masks in `xfs_fs.h`.
- `struct xfs_group` stores group health fields under kernel builds.

## Invariants
- Runtime code should call `mark_sick` when observing corruption without implying full checking.
- Fsck/scrub tools should use `mark_corrupt` when a checked object is corrupt and `mark_healthy` after successful repair.
- Secondary evidence can be forgotten when primary problems are fixed.
- Indirect evidence indicates a problem elsewhere after resource/context release.

## Notable Risks
- Masks must remain coordinated with userspace reporting masks and health monitor conversion functions.
- Misclassifying primary vs secondary vs indirect evidence can either over-report repairs or hide root causes.
