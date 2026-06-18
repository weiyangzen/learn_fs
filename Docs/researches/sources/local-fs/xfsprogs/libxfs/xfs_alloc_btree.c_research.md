# File Research: sources/local-fs/xfsprogs/libxfs/xfs_alloc_btree.c

## Purpose

`xfs_alloc_btree.c` adapts the generic XFS btree engine to the two allocation free-space btrees: bnobt, ordered by start block, and cntbt, ordered by block count then start block. It defines cursor operations, block allocation/free callbacks, record/key comparisons, verifiers, buffer ops, cursor constructors, staged btree commit support, max record/height calculations, and cursor cache lifecycle.

## Cursor and Block Callbacks

- `xfs_bnobt_dup_cursor` and `xfs_cntbt_dup_cursor` duplicate cursors by reinitializing with the same mount, transaction, AGF buffer, and perag.
- `xfs_allocbt_set_root` writes a new root pointer and adjusts AGF/perag levels for either bno or cnt trees, then logs AGF roots/levels.
- `xfs_allocbt_alloc_block` allocates btree blocks from the AGFL via `xfs_alloc_get_freelist`, increments `m_allocbt_blks`, marks busy extents reusable, and returns a short pointer.
- `xfs_allocbt_free_block` returns a btree block to AGFL via `xfs_alloc_put_freelist`, decrements `m_allocbt_blks`, and inserts a busy extent with discard skipped.
- `xfs_allocbt_get_minrecs` and `xfs_allocbt_get_maxrecs` read per-level record limits from mount geometry.

## Record, Key, and Pointer Encoding

- `xfs_allocbt_init_key_from_rec` copies start block and block count from record to key.
- `xfs_bnobt_init_high_key_from_rec` computes high key as last block in the free extent.
- `xfs_cntbt_init_high_key_from_rec` uses block count as the high key dimension.
- `xfs_allocbt_init_rec_from_cur` serializes cursor in-core allocation record to disk record.
- `xfs_allocbt_init_ptr_from_cur` initializes root pointer from AGF root fields, asserting cursor group and AGF sequence match.

## Ordering Semantics

bnobt:
- `xfs_bnobt_cmp_key_with_cur` compares key start block to cursor start block.
- `xfs_bnobt_cmp_two_keys` compares start blocks.
- `xfs_bnobt_keys_inorder` requires strictly increasing start blocks.
- `xfs_bnobt_recs_inorder` allows adjacent extents but not overlap: first start + count <= second start.
- `xfs_allocbt_keys_contiguous` supports key-contiguity checks for bnobt startblock keys.

cntbt:
- `xfs_cntbt_cmp_key_with_cur` compares block count, then start block.
- `xfs_cntbt_cmp_two_keys` compares block count, then start block.
- `xfs_cntbt_keys_inorder` and `xfs_cntbt_recs_inorder` enforce count/start ordering.
- `keys_contiguous` is unused for cntbt.

## Verification and Buffer Ops

`xfs_allocbt_verify` checks:
- btree magic via buffer ops.
- v5 AG btree header if CRC is enabled.
- tree level against perag initialized levels where possible.
- online repair temporary levels when enabled.
- mount maximum alloc btree levels when perag is unavailable or not initialized.
- generic AG btree block structure against max records for the level.

`xfs_allocbt_read_verify` validates CRC and structure, reporting corruption through verifier errors and tracepoints. `xfs_allocbt_write_verify` validates structure and writes CRC.

The file exports:
- `xfs_bnobt_buf_ops`
- `xfs_cntbt_buf_ops`

These identify names, magic values, read/write verifiers, and structural verifier callbacks.

## Btree Operation Tables

`xfs_bnobt_ops` and `xfs_cntbt_ops` fill `struct xfs_btree_ops` for generic btree code. Both are AG btrees with short pointers and allocation record/key sizes. They set LRU refs, stats offsets, health sick masks, cursor duplication, root setting, block allocation/free, min/max records, record/key init, pointer init, key comparisons, buffer ops, ordering checks, and optional key contiguity.

The key difference is ordering: bnobt is ordered by start block and can reason about contiguous startblock keys; cntbt is ordered by extent length then start block.

## Cursor Constructors

- `xfs_bnobt_init_cursor` allocates a generic btree cursor with bnobt ops, holds the perag group, stores the AGF buffer, and initializes levels from `agf_bno_level` when an AGF buffer is supplied.
- `xfs_cntbt_init_cursor` does the same for cntbt and `agf_cnt_level`.

Both support staging cursors where transaction and AGF buffer can be `NULL`.

## Staging and Size Calculations

- `xfs_allocbt_commit_staged_btree` installs a staged fake-root tree into AGF root/level fields, logs AGF root/level changes, and commits the fake root through generic staging code.
- `xfs_allocbt_block_maxrecs` computes leaf or internal record capacity after header removal.
- `xfs_allocbt_maxrecs` subtracts the allocation btree block header and returns per-block capacity.
- `xfs_allocbt_maxlevels_ondisk` computes worst-case free-space btree height from minimum block sizes and maximum fragmented free-space records.
- `xfs_allocbt_calc_size` uses generic btree sizing with mount allocation min-record arrays.

## Cache Lifecycle

- `xfs_allocbt_init_cur_cache` creates the allocation btree cursor cache sized for the maximum on-disk height.
- `xfs_allocbt_destroy_cur_cache` destroys it and clears the pointer.

## Invariants and Risks

- Btree block allocation and freeing must use AGFL and keep AGF/perag btree block counters coherent.
- Verifier max-level logic must tolerate growfs and log recovery contexts where perag state is absent or not fully initialized.
- Repair can rewrite btrees with alternate temporary levels, so verifier logic has conditional repair allowances.
- bnobt and cntbt have identical record layout but different comparison semantics; mixing op tables would corrupt allocator behavior.
