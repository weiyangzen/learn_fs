# File Research: sources/os/linux/linux-stable/fs/gfs2/rgrp.c

## Scope

This file implements GFS2 resource group indexing, bitmap interpretation, block reservation, allocation/freeing, rgrp LVB synchronization, rgrp verification, FITRIM/discard, and rgrp-list locking helpers. It is the central allocator implementation behind `gfs2_inplace_reserve()`, `gfs2_alloc_blocks()`, dinode unlink/free paths, and extent/xattr metadata frees.

## Public And Internal APIs Covered

- Public rgrp lookup and traversal: `gfs2_blk2rgrpd()`, `gfs2_rgrpd_get_first()`, `gfs2_rgrpd_get_next()`, `check_and_update_goal()`.
- Rindex/rgrp lifecycle: `gfs2_rindex_update()`, `gfs2_ri_total()`, `gfs2_clear_rgrpd()`, `gfs2_rgrp_go_instantiate()`, `gfs2_rgrp_brelse()`, `gfs2_free_clones()`.
- Reservation APIs: `gfs2_inplace_reserve()`, `gfs2_inplace_release()`, `gfs2_rs_deltree()`, `gfs2_rs_delete()`.
- Allocation/free APIs: `gfs2_alloc_blocks()`, `__gfs2_free_blocks()`, `gfs2_free_meta()`, `gfs2_unlink_di()`, `gfs2_free_di()`, `gfs2_check_blk_type()`.
- Discard and diagnostics: `gfs2_rgrp_send_discards()`, `gfs2_fitrim()`, `gfs2_rgrp_verify()`, `gfs2_rgrp_dump()`.
- Rgrp list helpers: `gfs2_rlist_add()`, `gfs2_rlist_alloc()`, `gfs2_rlist_free()`, `rgrp_lock_local()`, `rgrp_unlock_local()`.

## Control Flow And Behavior

Resource group bitmap state is encoded as two bits per data block: free, used data, unlinked dinode, or used metadata/dinode. `gfs2_setbit()` enforces legal state transitions with `valid_change[]` and reports consistency failures with rgrp details before withdrawing. `gfs2_testbit()`, `gfs2_bit_search()`, `gfs2_bitfit()`, `gfs2_rbm_from_block()`, and `gfs2_rbm_add()` provide the low-level bitmap cursor machinery.

`gfs2_rindex_update()` locks the rindex inode if needed, then `read_rindex_entry()` allocates `gfs2_rgrpd` objects, initializes their rgrp glocks, computes bitmap descriptors with `compute_bitstructs()`, and inserts them into `sd_rindex_tree`. `set_rgrp_preferences()` marks node-local preferred rgrps based on journal id to reduce cluster contention.

Rgrp instantiation reads all bitmap/header blocks through the rgrp glock, validates metadata types, loads on-disk counters into `rd_free`, `rd_dinodes`, and `rd_igeneration`, initializes `rd_free_clone` and allocation failure state, and either initializes or validates the rgrp LVB. `update_rgrp_lvb()` can satisfy rgrp state from a valid LVB when `ar_rgrplvb` is enabled.

`gfs2_inplace_reserve()` searches up to three passes for an rgrp that can satisfy `ap->target` or later `ap->min_target`. It starts from an active reservation or inode goal, optionally applies Orlov directory skipping, avoids contended rgrp glocks using glock timing statistics, reclaims unlinked dinodes via `try_rgrp_unlink()`, flushes the log before the final pass, and records `rs_reserved` against `rd_reserved`.

Reservation discovery uses `rg_mblk_search()` and `gfs2_rbm_find()`. The search uses clone bitmaps when avoiding newly freed blocks, skips `GBF_FULL` bitmap blocks, respects other inodes' reservation ranges through `gfs2_next_unreserved_block()`, and updates `rd_extfail_pt` when no extent large enough exists. If a smaller but usable maximum extent is found, the minimum request is reduced to that extent.

`gfs2_alloc_blocks()` takes the local rgrp mutex, searches within the active reservation first and then without reservation, marks one dinode block or data/metadata blocks through `gfs2_alloc_extent()`, updates inode goal fields, consumes reservation accounting, decrements free counters, writes the rgrp header/LVB with `gfs2_rgrp_out()`, updates statfs and quota, and removes revokes for new dinode allocations. Any impossible allocation after reservation marks the rgrp readonly until unmount.

Freeing uses clone bitmaps. `rgblk_free()` allocates `bi_clone` lazily, copies the live bitmap into it, journals the bitmap buffer, then changes live bits. `__gfs2_free_blocks()` clears bitmap state, increments `rd_free`, clears the trimmed flag, writes the rgrp header, and wipes journal state for metadata/jdata/directory blocks. `gfs2_unlink_di()` changes a dinode to `UNLINKED` and increments `rl_unlinked`; `gfs2_free_di()` later returns it to free space and decrements dinode/unlinked counters.

FITRIM checks privileges, live journal state, discard capability, and rindex freshness, then locks each rgrp exclusively and submits discards for free ranges found by comparing clone/current bitmap state. Successfully trimmed rgrps are journaled with `GFS2_RGF_TRIMMED`; discard errors disable the mount's discard option.

## State And Data Structures

- `struct gfs2_rbm` is a cursor of rgrp, bitmap index, and bitmap-relative offset.
- `struct gfs2_extent` stores a candidate cursor plus length for fallback extent selection.
- `struct gfs2_rgrpd` state maintained here includes `rd_bits`, `rd_gl`, `rd_rgl`, `rd_flags`, `rd_free`, `rd_free_clone`, `rd_dinodes`, `rd_igeneration`, `rd_requested`, `rd_reserved`, `rd_extfail_pt`, `rd_last_alloc`, `rd_rstree`, and `rd_mutex`.
- `struct gfs2_blkreserv` ranges are kept in an rbtree per rgrp and carry `rs_start`, `rs_requested`, `rs_reserved`, and `rs_rgd`.
- Bitmap block state flags include `GBF_FULL`; rgrp flags include on-disk flags, preferred/error/check masks, and `GFS2_RGF_TRIMMED`.

## Dependencies

The file depends on GFS2 glocks, rindex internal reads, meta I/O, transactions, quotas, statfs, log flushing, rgrp LVBs, inode goals, journal wipes, glock statistics, and tracepoints. It also uses Linux rbtrees, buffer heads, discard APIs, capability checks, and user copy for `FITRIM`.

## Risks And Invariants

Allocation correctness depends on synchronizing the rgrp glock, local `rd_mutex`, reservation spinlock, clone bitmaps, transaction metadata buffers, and rgrp header/LVB counters. `rd_free`, `rd_free_clone`, `rd_requested`, and `rd_reserved` must never drift. Clone bitmaps intentionally prevent immediate reallocation of recently freed blocks before journal safety. `gfs2_check_blk_type()` relies on the inode glock for dinode synchronization and only makes sense for dinode/unlinked checks. Rgrp LVB mode can skip disk reads only when LVB magic and counters are valid. `rd_extfail_pt` is a performance hint and must not exclude allocations after reservations or frees change availability.
