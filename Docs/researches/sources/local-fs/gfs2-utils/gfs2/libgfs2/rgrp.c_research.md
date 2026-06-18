# File Research: sources/local-fs/gfs2-utils/gfs2/libgfs2/rgrp.c

This file implements resource group planning, representation, bitmap buffer management, on-disk read/write, and extent search/allocation.

Major APIs:
- Geometry and lookup: `lgfs2_compute_bitstructs()`, `lgfs2_blk2rgrpd()`, `lgfs2_rgblocks2bitblocks()`, `lgfs2_rgsize_for_data()`.
- Resource group handles: `lgfs2_rgrps_init()`, `lgfs2_rgrps_free()`, `lgfs2_attach_rgrps()`.
- Planning/alignment: `lgfs2_rgrp_align_addr()`, `lgfs2_rgrp_align_len()`, `lgfs2_rgrps_plan()`, `lgfs2_rindex_entry_new()`.
- Rindex import: `lgfs2_rindex_read_fd()`, `lgfs2_rindex_read_one()`, `lgfs2_rgrps_append()`.
- I/O: `lgfs2_rgrp_bitbuf_alloc/free()`, `lgfs2_rgrp_read()`, `lgfs2_rgrp_relse()`, `lgfs2_rgrp_write()`, `lgfs2_rgrps_write_final()`.
- Tree iteration: `lgfs2_rgrp_first/last/next/prev()`, `lgfs2_rgrp_insert()`, `lgfs2_rgrp_free()`.
- Bitmap extents: `lgfs2_rbm_from_block()`, `lgfs2_rbm_find()`, `lgfs2_alloc_extent()`.

Important behavior:
- Computes first bitmap block differently from subsequent bitmap blocks because rgrp and bitmap metadata headers differ.
- Stores resource groups in red-black trees.
- Plans one or two resource-group lengths to fit available space while respecting alignment.
- Reads/writes resource group headers and bitmap blocks, validating metadata headers and CRC.
- Searches for free extents using fast byte-aligned bitmap scanning plus unaligned edge handling.
- Allocates extents by setting first block state to dinode/used and remaining blocks used.

Risk notes:
- Alignment math directly affects grow/mkfs layout.
- `lgfs2_rbm_find()` assumes `minext` is non-null even though comment mentions NULL.
- `lgfs2_rgrp_write()` may write rounded-up alignment padding length from the bitmap buffer.
- Dirty bitmap release writes each modified bitmap block individually and logs but does not return write failure.
- Resource group ownership differs between `lgfs2_rgrp_free()` on `sdp->rgtree` and `lgfs2_rgrps_free()` on a handle.
