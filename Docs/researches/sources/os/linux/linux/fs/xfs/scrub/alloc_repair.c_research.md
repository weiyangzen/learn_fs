# File Research: sources/os/linux/linux/fs/xfs/scrub/alloc_repair.c

This file repairs the XFS free-space btrees by reconstructing both bnobt and cntbt from reverse mapping data. It treats the rmapbt as authoritative for used space, derives free space from gaps in rmap records, stages replacement btrees, commits them into the AGF, and reaps old btree blocks.

`xrep_setup_ag_allocbt` flushes the AG busy extent list because repair cannot safely put the same extents on the busy list twice. The main repair context `struct xrep_abt` tracks OWN_AG blocks, blocks known not to be old allocbt blocks, staged new btrees, free-space records in an `xfarray`, free block totals, and longest extent length.

Collection is performed by `xrep_abt_find_freespace`. It walks all rmap records, records OWN_AG extents, records the current rmapbt path, detects gaps between physical mappings as free space, adds the trailing gap to EOAG, scans AGFL blocks, and subtracts current rmapbt/AGFL metadata from OWN_AG to identify possible old bnobt/cntbt blocks. Candidate free extents are checked against inode chunks and refcount/shared/CoW state before being stashed.

Rebuild uses an iterative reservation algorithm. Free extents are sorted by length, btree geometry is estimated, blocks are reserved from the discovered free records, and the process repeats until sufficient space exists for both new trees. The code then bulk-loads cntbt by length order and bnobt by block-number order, installs staged roots in the AGF, resets AGF free-space counters, updates alternate perag btree heights to avoid verifier races with old blocks, disposes of unused reservations, rolls the transaction, and reaps old allocation-btree blocks.

`xrep_revalidate_allocbt` reruns scrub of both bnobt and cntbt after repair, temporarily changing scrub type so tree-to-tree xrefs run in both directions. The file depends on rmapbt; without it, online repair is unsupported.
