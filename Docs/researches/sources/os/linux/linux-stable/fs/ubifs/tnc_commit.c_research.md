# File Research: sources/os/linux/linux-stable/fs/ubifs/tnc_commit.c

## Purpose
Implements TNC commit mechanics: collecting dirty znodes, assigning on-flash index positions, optionally writing into obsolete gaps, writing index nodes, updating hashes/lprops, and finalizing clean/obsolete znode state.

## Key Behavior
- `get_znodes_to_commit()` builds a circular commit list from dirty znodes, marks them COW, stores commit-parent metadata, and verifies dirty count consistency.
- `alloc_idx_lebs()` estimates and reserves empty LEBs for the new index; debug mode can force `-ENOSPC` to test in-the-gaps behavior.
- `layout_in_empty_space()` assigns positions to dirty znodes in the index head and newly allocated index LEBs, updating parent/root references and lprops.
- `layout_in_gaps()` scans dirty index LEBs, identifies obsolete index-node gaps, and writes new index nodes into reusable space when empty LEB allocation is insufficient.
- `make_idx_node()` serializes a znode into an index node, calculates hashes, records old index references, updates parent/root branches, clears dirty/COW state under the TNC mutex, and updates calculated index size.
- `ubifs_tnc_start_commit()` validates TNC, builds the commit list, lays out positions, frees unused index LEBs, saves dirty index LEB numbers, updates budgeting’s committed index size, and returns the new root branch.
- `write_index()` serializes and writes index nodes laid out in empty space, updates branch hashes under `tnc_mutex`, clears dirty/COW flags with memory barriers, and advances the index head.
- `ubifs_tnc_end_commit()` returns gap LEBs, writes the index, frees obsolete znodes, clears `c->cnext`, and frees allocated index LEB arrays.

## Important Dependencies
- Uses `ubifs_scan()` from `scan.c` for in-the-gaps LEB analysis.
- Uses TNC membership helpers from `tnc.c`: `is_idx_node_in_tnc()` and old-index insertion.
- Updates lprops through `ubifs_update_one_lp()`, `ubifs_change_one_lp()`, and dirty-index LEB tracking.
- Depends on commit state shared with foreground TNC mutation and shrinker code.

## Invariants and Risks
- The previous committed index must remain intact until the new index is durably committed; old-index RB-tree tracking enforces this for hard-to-find obsolete nodes.
- Dirty flags must become visible as cleared before COW flags, hence explicit memory barriers in `write_index()`.
- Clean znode counter increments are delayed until obsolete znodes are freed under `tnc_mutex`, avoiding races with foreground dirtying.
- Gap commits require atomic in-place LEB update semantics via `ubifs_leb_change()`.
- Layout and write phases cross-check expected znode positions and index head offsets to catch commit accounting bugs.
