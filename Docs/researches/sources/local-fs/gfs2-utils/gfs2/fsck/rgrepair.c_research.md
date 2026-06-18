# File Research: sources/local-fs/gfs2-utils/gfs2/fsck/rgrepair.c

This file repairs damaged GFS2 resource-group indexes and resource-group headers/bitmap blocks. It supports multiple trust levels for the existing rindex: accept it, sanity-copy it, calculate an expected mkfs-style layout, or rebuild by scanning the device.

The public entry point is `rindex_repair(struct fsck_cx *cx, int trust_lvl, int *ok)`. Depending on `trust_lvl`, it calls:
- `expect_rindex_sanity()` when the rindex seems sane.
- `rindex_calculate()` to compute expected RG layout from device geometry and rindex count.
- `rindex_rebuild()` to scan for RGs, including uneven layouts from converted/grown GFS filesystems.

Important helper paths:
- `find_journaled_rgs()` scans journal contents and records RG-looking false positives so journaled RG copies are ignored during rebuild.
- `find_shortest_rgdist()` samples RG spacing and detects grow segments.
- `find_next_rgrp_dist()` and `hunt_and_peck()` infer uneven or damaged next-RG distances.
- `compute_rgrp_layout()` and `calc_rgrps()` build expected `lgfs2_rgrp_tree` entries.
- `rewrite_rg_block()` reconstructs missing/corrupt RG or RB headers after user approval.

After building expected data in `rgcalc`, `rindex_repair()` rereads the on-disk rindex, handles invalid rindex size, compares actual and expected entries, writes fixed entries through `lgfs2_writei()`, recomputes bitmap structures, then reads actual resource groups and repairs damaged RG/RB blocks.

Dependencies include libgfs2 geometry/rgrp APIs, journal initialization/recovery helpers, special-block tracking, direct `pread`/`pwrite`, and fsck query/logging.

Risks and notes:
- Rebuild logic assumes maximum RG size constraints and uses heuristics/tolerances; too many discrepancies abort the chosen repair level.
- It frees and rebuilds `sdp->rgtree` in several modes, so callers must expect rgrp state invalidation.
- Repairs occur before normal pass allocation is available, so the code cannot grow the rindex beyond existing file space.
