# File Research: sources/local-fs/jfsutils/fsck/fsckbmap.c

This module verifies and rebuilds the JFS aggregate block allocation map. It compares on-disk dmap/pmap and summary-tree structures against fsck’s workspace block bitmap, rebuilds those structures when repair is approved, and reports summary diagnostics. It depends on global `sb_ptr`, `agg_recptr`, and `bmap_recptr`, plus block-map constants and helpers from `diskmap.h` and `xfsckint.h`.

The file uses `struct fsck_stree_proc_parms` to pass summary-tree context: buffer tree, buffer/workspace summary arrays, leaf counts, leaf index, minimum buddy value, page level/order, and error flags. The same helper path handles dmap trees and higher-level L0/L1/L2 dmapctl trees.

Control-page handling is split between `ctlpage_verify()` and `ctlpage_rebuild()`. Verification reads the block-map control page, swaps it for host endian, and checks mapsize, free-block count, log2 blocks-per-page, allocation-group count, max level, highest active AG, preferred AG, AG geometry fields, max free buddy, and per-AG free lists. Rebuild recomputes all of those fields from fsck state, picks a valid preferred AG when needed, copies `AGFree_tbl`, swaps back, and writes the page.

Dmap pmap handling is split between `dmap_pmap_verify()` and `dmap_pwmap_rebuild()`. Both locate the corresponding section of fsck’s workspace bitmap using `blkmap_find_bit()` and `blkmap_get_page()`. Rebuild copies workspace bits into both `wmap` and `pmap`, computes each word’s max buddy value, counts free and used blocks, and updates aggregate counters. Verify computes the same workspace-derived truth, compares every bit against on-disk `pmap`, records ranges where pmap is unexpectedly on or off, sets `dmap_pmap_error`, and updates aggregate free/used counters.

`dmappg_verify()` and `dmappg_rebuild()` operate on complete dmap pages. They fetch the page by first block, validate or set `start`, `nblocks`, and `nfree`, handle phantom blocks beyond aggregate size, update total free blocks and per-AG free tables, mark active allocation groups, and verify or rebuild the dmap summary tree.

`dmap_tree_verify()` and `dmap_tree_rebuild()` process the dmap’s local buddy summary tree. Verification first checks tree specification fields (`dmt_nleafs`, `dmt_l2nleafs`, `dmt_leafidx`, height, and `budmin`), then calls `stree_verify()`. Rebuild initializes those fields and calls `stree_rebuild()`.

`Ln_tree_verify()` and `Ln_tree_rebuild()` perform the same work for L0, L1, and L2 summary pages. They select the correct workspace leaf/tree arrays and error flags by level, use `LPERCTL`, `L2LPERCTL`, `CTLLEAFIND`, height 5, and buddy minimum `L2BPERDMAP + level * L2LPERCTL`, and read/write pages through `blktbl_Ln_page_get()` and `blktbl_Ln_page_put()`.

`rebuild_blkall_map()` is the full repair path. It initializes block-map fsck state, flushes pending IAG writes because the dmap buffer aliases IAG storage, walks every dmap page, rebuilds dmap pages, feeds dmap root values into L0 workspace leaves, rebuilds L0/L1/L2 pages as leaf sets fill, handles partial final pages by padding leaves with `-1`, and finally rebuilds the control page.

`verify_blkall_map()` is the full validation path. It follows the same traversal shape as rebuild but compares each dmap and summary page instead of rewriting it, then verifies the control page and calls `verify_blkall_summary_msgs()`.

`stree_rebuild()` copies workspace leaf values into the buffer tree and calls `ujfs_adjtree()` to rebuild internal nodes and root. `stree_verify()` calls `ujfs_adjtree()` on the workspace tree and then compares buffer internal nodes and leaves separately, setting distinct leaf/internal error flags and emitting detailed messages.

`init_bmap_info()` zeroes and initializes `bmap_recptr`, sets eyecatchers, assigns buffer pointers into aggregate workspace buffers, computes total block counts and page counts, initializes AG state, counters, current page ordinals/indices, and error flags.

`verify_blkall_summary_msgs()` emits one summary message per detected class of dmap, L0, L1, L2, or control-page error. It marks `agg_recptr->ag_dirty` when allocation map or control metadata is bad.

The important design pattern is “workspace truth first”: earlier fsck passes mark allocated blocks in an independent workspace bitmap, and this module either reconciles on-disk allocation metadata to that truth or reports divergence. The key risk areas are global state sequencing, endian swap boundaries, partial-page padding with `-1`, and shared buffer aliasing with inode allocation group processing.
