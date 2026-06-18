# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/agheader.c

## Purpose
Implements online scrub checks for XFS allocation group header metadata: secondary superblocks, AGF, AGFL, and AGI. It validates header fields against mounted primary filesystem state, verifies per-AG counters and root pointers, and cross-references header-owned blocks with free space, inode, reverse-map, refcount, shared, and CoW staging metadata.

## Main Entry Points
- `xchk_setup_agheader`: enables intent drain if needed and sets up filesystem-wide scrub context.
- `xchk_superblock`: checks secondary superblocks only; AG 0 is trusted because mount already validated the primary superblock.
- `xchk_agf`: checks allocation group free-space header geometry, btree roots, levels, AGFL counters, and in-core perag counters.
- `xchk_agfl`: reads AGFL, walks listed free-list blocks, validates uniqueness and ownership.
- `xchk_agi`: checks inode allocation header geometry, inobt/finobt roots and levels, inode counters, inode pointer fields, unlinked buckets, and in-core perag counters.

## Key Behavior
`xchk_superblock` compares secondary superblock fields against `mp->m_sb`, separating hard corruption from preen-only drift. Immutable mkfs geometry and feature bits become corruption; mutable or repairable fields such as UUID propagation, quota inodes, labels, and some feature synchronization mismatches are marked preen. It also checks trailing bytes beyond the active superblock format are zero according to mounted features such as crc, metauuid, metadir, and zoned support.

`xchk_agf_xref` initializes AG btree cursors and confirms the AGF block is used, not an inode chunk, owned only by filesystem metadata, not shared, and not CoW staging. It recalculates `agf_freeblks` from bnobt, `agf_longest` from cntbt, btree block counters from bnobt/cntbt/rmapbt, and refcount block count from refcountbt.

`xchk_agfl` verifies the AGFL header block itself, then walks AGFL entries through `xfs_agfl_walk`. Valid entries must be valid AG blocks, owned as AG metadata, not shared or CoW staging, and unique after sorting. It detects AGF `agf_flcount` overflow beyond `xfs_agfl_size`.

`xchk_agi` validates AGI fields, checks inode btree roots/levels, validates inode count/freecount bounds, verifies newino/dirino/unlinked bucket aginos, and walks incore unlinked lists to catch bad bucket assignment or missing/unlinked-state mismatches.

## Dependencies and Interactions
Uses XFS scrub common helpers, allocation btrees, ialloc btrees, rmap/refcount cross-reference helpers, perag state, superblock feature helpers, and buffer recheck helpers. This file is the validation side paired with `agheader_repair.c`.

## Failure Handling
Verifier/read errors from secondary superblock reads are normalized to scrub corruption where appropriate. Cross-reference checks are skipped once primary corruption is already flagged. `-ECANCELED` is used internally by AGFL walking to stop after corruption without surfacing as a hard syscall error.
