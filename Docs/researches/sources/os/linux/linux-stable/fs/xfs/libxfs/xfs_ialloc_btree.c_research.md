# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_ialloc_btree.c

## Role in the repository

`xfs_ialloc_btree.c` implements the concrete generic-btree operations for the XFS inode allocation btree and free inode btree. It supplies cursor construction, root updates, block allocation/freeing, key and record initialization, ordering checks, verifiers, fanout calculations, staged btree commits, sparse allocation mask conversion, FINOBT reservation calculations, and cursor cache lifecycle.

## Cursor and root operations

`xfs_inobt_init_cursor` and `xfs_finobt_init_cursor` allocate generic btree cursors with INOBT or FINOBT ops, hold the per-AG group, attach the AGI buffer, and initialize cursor height from `agi_level` or `agi_free_level`.

Root callbacks update:
- `agi_root` and `agi_level` for INOBT;
- `agi_free_root` and `agi_free_level` for FINOBT.

Both root updates log the corresponding AGI fields.

## Block allocation, freeing, and counters

INOBT block allocation uses normal AG reservation, while FINOBT allocation uses metadata reservation unless the mount has `m_finobt_nores` set. New btree blocks are allocated near the requested start block and recorded as INOBT-owned rmap extents.

Freeing schedules one btree block for deferred freeing with the same owner and reservation policy.

`xfs_inobt_mod_blockcount` updates `agi_iblocks` or `agi_fblocks` when the INOBT block count feature is enabled, logging `XFS_AGI_IBLOCKS` because the AGI bit covers both counters.

## Btree operation callbacks

The INOBT and FINOBT ops share record/key logic:
- min/max records come from inode geometry fanout arrays;
- keys are initialized from `ir_startino`;
- high keys cover `ir_startino + XFS_INODES_PER_CHUNK - 1`;
- records are initialized from the cursor’s incore inode record, using sparse fields only when the filesystem supports sparse inodes;
- pointer initialization reads either `agi_root` or `agi_free_root`;
- key comparisons order by start inode;
- record ordering requires non-overlapping inode chunks.

The two operation tables differ primarily in name, stats offset, sick mask, root field, pointer root, buffer ops, and reservation behavior.

## Verification

`xfs_inobt_verify` checks magic, optional v5 AG btree header fields, level bounds against inode geometry, and generic AG btree block record counts. Read verification also checks CRC for CRC-enabled metadata and traces corrupt btree buffers on error. Write verification validates structure and recalculates AG btree CRCs.

`xfs_inobt_buf_ops` accepts INOBT magic values; `xfs_finobt_buf_ops` accepts FINOBT magic values. Both share verifier functions because their layout and rules are the same.

## Staged btree commit

`xfs_inobt_commit_staged_btree` installs a staged rebuilt INOBT or FINOBT root into the AGI. It copies fake-root block, level, and optional block count fields into AGI, logs the affected fields, and commits the staged root to the generic btree layer. This is used by rebuild/repair code.

## Geometry and sizing

`xfs_inobt_maxrecs` computes leaf or internal node fanout after subtracting the correct short-form btree header size. `xfs_iallocbt_maxlevels_ondisk` computes the maximum possible on-disk height across INOBT and FINOBT using minimum block sizes and worst-case inode record count.

`xfs_iallocbt_calc_size` wraps generic btree sizing for a given record count.

## Sparse inode helpers

`xfs_inobt_irec_to_allocmask` expands the sparse record holemask into a 64-bit physical inode allocation bitmap. Holemask zero bits mean physical inode regions exist, so the helper inverts the 16-bit holemask and expands each set holemask bit into multiple inode bits.

`xfs_inobt_rec_check_count`, enabled for debug or warning builds, verifies that the expanded allocation bitmap contains the same number of physically allocated inodes as `ir_count`.

## FINOBT reservation accounting

`xfs_finobt_calc_reserves` computes how many blocks to reserve for FINOBT growth and how many are currently used. If INOBT block counts are available it reads `agi_fblocks`; otherwise it counts blocks by traversing the FINOBT. The requested reservation is based on a maximum possible btree size for the AG.

## Cursor cache lifecycle

`xfs_inobt_init_cur_cache` creates the slab cache sized for the maximum INOBT cursor height. `xfs_inobt_destroy_cur_cache` destroys it during teardown.

## Important invariants

- INOBT and FINOBT are short-pointer AG btrees.
- FINOBT has the same record format as INOBT but tracks only records with free inodes.
- Btree block counters are updated only when the inobtcounts feature is enabled.
- Sparse record count and holemask consistency is checked independently of logical freecount.
- Growfs and log recovery can limit verifier assumptions about fully initialized per-AG state.
