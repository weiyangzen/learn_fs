# File Research: sources/os/linux/linux/fs/gfs2/glops.h

## Scope

Header exporting glock operation descriptors and glock operation helper APIs.

## APIs

- Declares global freeze workqueue `gfs2_freeze_wq`.
- Exports all glock operation tables used by glock creation and lock-type dispatch.
- Exports `gfs2_glops_list[]`, indexed by lock type.
- Declares `gfs2_inode_metasync()` and `gfs2_ail_flush()`.

## Invariants

- Consumers select behavior by lock type through these operation tables.
- Only the declarations live here; callback behavior is implemented in `glops.c`.
