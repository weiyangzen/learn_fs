# File Research: sources/local-fs/gfs2-utils/gfs2/fsck/pass5.c

This file implements `fsck.gfs2` pass 5, resource-group bitmap reconciliation. It compares fsck’s reconstructed block map against each on-disk resource group bitmap, optionally fixes mismatched bitmap states, and updates resource-group free/dinode counters.

`pass5(struct fsck_cx *cx, struct bmap *bl)` iterates `sdp->rgtree`, calling `update_rgrp()` for each resource group. `update_rgrp()` walks all bitmap buffers in the resource group and invokes `check_block_status()`, then compares counted free/dinode totals with `rt_free` and `rt_dinodes`.

`check_block_status()` decodes two-bit GFS2 bitmap entries, maps each block to fsck’s `block_type(bl, block)`, increments count buckets, and handles discrepancies. Blocks seen as `GFS2_BLKST_UNLINKED` are treated specially: they can be reclaimed to free, but are not automatically considered corruption because cluster deletion/open races can leave such blocks temporarily.

Dependencies include `libgfs2`, fsck context, bitmap helpers from `util.h`, resource-group structures, and interactive query handling.

Risks and notes:
- `count[5]` preserves room for legacy `GFS1_BLKST_USEDMETA`.
- If resource-group total data count does not equal the sum of counted states, the code treats it as an internal fsck error and exits.
- Counter updates mark the first bitmap buffer modified through `lgfs2_rgrp_out()`.
