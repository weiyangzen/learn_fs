# File Research: sources/os/linux/linux-stable/fs/gfs2/glops.h

## Scope

This header exports glock operation tables and the small set of glops helpers used outside `glops.c`.

## APIs

- Declares `gfs2_freeze_wq`.
- Declares operation tables for meta, inode, rgrp, freeze, iopen, flock, nondisk, quota, and journal glocks.
- Declares `gfs2_glops_list[]` for type-indexed lookup.
- Declares `gfs2_inode_metasync()` and `gfs2_ail_flush()`.

## Dependencies And Role

- Included by glock, file, inode, and other subsystem files that need specific glops instances for `gfs2_glock_get()` or need to flush inode metadata/AIL state.
- Depends on `incore.h` for glock and inode structure declarations.

## Risks And Invariants

- The exported operation tables are the binding between lock type numbers and behavior. Mismatching a glock type with the wrong table would corrupt lock-state semantics.
- `gfs2_ail_flush()` is used by fsync-style paths and must preserve the AIL/log ordering implemented in `glops.c`.
