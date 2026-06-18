# File Research: sources/os/linux/linux-stable/fs/gfs2/rgrp.h

## Scope

This header declares the GFS2 resource group allocator interface used by inode, metadata, xattr, statfs, and trim paths. It also defines reservation tuning constants and inline helpers for reservation/rgrp membership tests.

## APIs And Definitions

- Reservation constants: `RGRP_RSRV_MINBLKS` reserves at least one 64-bit bitmap word's worth of blocks, and `RGRP_RSRV_ADDBLKS` grows inode size hints when reservations are consumed.
- Lookup/lifecycle declarations cover rgrp tree lookup/traversal, rindex update, rgrp instantiate/release, clone cleanup, and rgrp verification/dumping.
- Allocation declarations expose inplace reservation/release, block allocation, block/dinode freeing, unlinked dinode marking, and block type validation.
- `struct gfs2_rgrp_list` stores a dynamic list of rgrps and matching glock holders for multi-rgrp operations such as xattr indirect deallocation.
- Trim declarations expose `gfs2_rgrp_send_discards()` and `gfs2_fitrim()`.
- Inline `gfs2_rs_active()` checks whether a reservation is in an rbtree via `RB_EMPTY_NODE()`.
- Inline `rgrp_contains_block()` checks whether a filesystem block lies in an rgrp's data span.

## Dependencies

The header uses Linux slab/uaccess declarations and GFS2 inode, rgrp, holder, buffer, and file structures through forward declarations or included headers.

## Risks And Invariants

Callers must not treat `rgrp_contains_block()` as matching bitmap/header padding; it only tests `[rd_data0, rd_data0 + rd_data)`. `gfs2_rs_active()` requires reservation nodes to be initialized with `RB_CLEAR_NODE()` when inactive. `gfs2_rg_blocks()` lives in `trans.h`, but callers using the allocation API must reserve enough transaction blocks for rgrp header/bitmap updates.
