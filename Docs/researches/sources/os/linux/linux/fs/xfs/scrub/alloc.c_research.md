# File Research: sources/os/linux/linux/fs/xfs/scrub/alloc.c

This file implements online scrub for XFS free-space btrees: bnobt and cntbt. `xchk_setup_ag_allocbt` prepares AG btree scrub state, optionally enables intent draining, and, when repair is available, performs allocation-btree repair setup.

The central record validator is `xchk_allocbt_rec`. It decodes an on-disk allocation btree record into `xfs_alloc_rec_incore`, validates the free-space extent with `xfs_alloc_check_irec`, detects adjacent mergeable free records that should have been coalesced, and cross-references the record against other metadata. Cross-reference checks require a matching record in the peer free-space btree: bnobt records must appear in cntbt and cntbt records must appear in bnobt with the same start block and length.

Additional xrefs assert that free extents are not inode chunks, have no rmap owner, are not shared blocks, and are not CoW staging blocks. The common helper `xchk_xref_is_used_space` is exported for other scrubbers in this group; it queries bnobt for records overlapping a supposedly allocated range and flags corruption if the range appears free.

Important invariants are that free-space records are physically valid, non-overlapping, non-adjacent when they could merge, mutually represented in both allocation btrees, and not claimed by inode, rmap, refcount, or CoW metadata. The code avoids xref work when the scrub item already carries primary corruption or xref skipping is requested.
