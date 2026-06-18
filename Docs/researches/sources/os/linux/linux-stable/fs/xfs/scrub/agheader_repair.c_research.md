# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/agheader_repair.c

## Purpose
Repairs XFS AG header structures: secondary superblocks, AGF, AGFL, and AGI. It reconstructs headers from trusted primary superblock/perag state and from rmap-discovered btree roots, updates in-core perag state, and rebuilds AGI unlinked inode lists.

## Main Entry Points
- `xrep_superblock`: rewrites a secondary superblock from AG 0 mounted state.
- `xrep_agf`: reconstructs AGF fields and btree root metadata.
- `xrep_agfl`: reconstructs AGFL contents from rmap-derived AG metadata ownership.
- `xrep_agi`: reconstructs AGI fields, inobt/finobt roots, inode counters, and unlinked buckets.

## Key Behavior
`xrep_superblock` refuses AG 0 repair, obtains the secondary superblock buffer, zeroes it, copies mounted superblock state, clears secondary-ignored `NEEDSREPAIR` and log incompat bits, sets buffer type, and logs the entire block.

AGF repair requires rmapbt. It reads the possibly corrupt AGF directly, reads AGFL as a filter, uses `xrep_find_ag_btree_roots` to find bnobt/cntbt/rmapbt/refcountbt roots, insists the found rmapbt root matches the old AGF, reinitializes the AGF header, implants found roots, recalculates free-space counters and btree block counts by walking/counting the btrees, logs the buffer, and reinitializes perag AGF state.

AGFL repair also requires rmapbt. It collects all `OWN_AG` extents, removes blocks known to belong to bnobt/cntbt/rmapbt paths, removes crosslinked blocks, limits the new free list to `xfs_agfl_size`, rewrites the AGFL header and entries, updates AGF `flfirst/fllast/flcount`, rolls the AG transaction, and reaps overflow blocks back to free space.

AGI repair requires rmapbt. It finds inobt/finobt roots via rmap data, rebuilds AGI header fields, counts inodes and inobt/finobt blocks, and reconstructs `agi_unlinked[]`. The unlinked rebuild is extensive: it walks old ondisk buckets, reloads missing inodes when needed, scans incore inode cache, scans inobt records for uncached unlinked inodes, stages next/prev links in xfarrays, reinserts lost unlinked inodes, logs forward links, fixes incore back links, and finally writes rebuilt bucket heads.

## Dependencies and Interactions
Uses `scrub/bitmap.h`, `agb_bitmap.h`, `agino_bitmap.h`, `reap.h`, `xfile.h`, `xfarray.h`, rmapbt discovery helpers, perag init bits, and transaction rolling. It depends on rmapbt for all AGF/AGFL/AGI rebuilds except secondary superblocks.

## Failure Handling
Each repair has a last termination check before committing. AGF/AGI preserve old headers and revert on failures before final commit. AGFL uses bitmaps to avoid freeing crosslinked blocks. AGI teardown destroys unlinked-list staging arrays and bitmap state.
