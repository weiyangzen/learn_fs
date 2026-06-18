# File Research: sources/os/bsd/freebsd-src/sys/ufs/ufs/inode.h

## Purpose
Defines the UFS in-core inode structure and helper macros for vnode conversion, dinode field access, inode flags, lazy timestamp/update behavior, and UFS1/UFS2 abstraction.

## Key Contents
- `struct iown_tracker` under `DIAGNOSTIC`:
  - Tracks ownership and stack traces for inode directory lookup side-effect fields.
- `struct inode`:
  - Vnode/mount identity: `i_vnode`, `i_ump`.
  - Quotas: `i_dquot[MAXQUOTAS]`.
  - Union for `i_dirhash` or snapshot block list.
  - On-disk dinode pointer union `i_dp`.
  - Inode number, flags, effective link count.
  - Directory lookup side-effect fields: `i_count`, `i_endoff`, `i_diroff`, `i_offset`.
  - Cluster write tracking.
  - Extended attribute transaction fields: `i_ea_area`, `i_ea_len`, `i_ea_error`, `i_ea_refs`.
  - Cached dinode fields: `i_size`, `i_gen`, `i_flags`, `i_uid`, `i_gid`, `i_nlink`, `i_mode`.
- Inode flags:
  - Timestamp/update: `IN_ACCESS`, `IN_CHANGE`, `IN_UPDATE`, `IN_MODIFIED`
  - Sync/lazy flags: `IN_NEEDSYNC`, `IN_LAZYMOD`, `IN_LAZYACCESS`
  - Extended attributes: `IN_EA_LOCKED`, `IN_EA_LOCKWAIT`
  - Journaling/truncation: `IN_TRUNCATED`
  - Format/state: `IN_UFS2`, `IN_IBLKDATA`, `IN_SIZEMOD`, `IN_ENDOFF`
- Flag helpers:
  - `UFS_INODE_SET_MODE`
  - `UFS_INODE_SET_FLAG`
  - `UFS_INODE_SET_FLAG_SHARED`
- Field aliases:
  - `i_dirhash`, `i_snapblklist`, `i_din1`, `i_din2`
- Mount/device/filesystem conversion macros:
  - `ITOUMP`, `ITODEV`, `ITODEVVP`, `ITOFS`, `ITOVFS`
- Format helpers:
  - `I_IS_UFS1`
  - `I_IS_UFS2`
- Dinode field access:
  - `DIP(ip, field)`
  - `DIP_SET(ip, field, val)`
  - `DIP_SET_NLINK`
- Snapshot and vnode helpers:
  - `IS_SNAPSHOT`
  - `IS_UFS`
  - `VTOI`, `VTOI_SMR`, `ITOV`
- Logical block path:
  - `struct indir`
- Softdep mount predicates:
  - `MOUNTEDSOFTDEP`, `DOINGSOFTDEP`
  - `MOUNTEDSUJ`, `DOINGSUJ`
- File handle overlay:
  - `struct ufid`
- Diagnostic wrappers for directory lookup side-effect fields:
  - `I_OFFSET`, `SET_I_OFFSET`
  - `I_COUNT`, `SET_I_COUNT`
  - `I_ENDOFF`, `SET_I_ENDOFF`

## Interactions
- Central in-core object used by UFS vnode operations, block mapping, ACLs, extattrs, quotas, dirhash, snapshots, and journaling.
- Includes `dinode.h`, `buf.h`, `seqc.h`, and queue/lock headers.
