# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/dmu_diff.c

## Role

`dmu_diff.c` implements the kernel side of ZFS snapshot difference reporting. It traverses the target snapshot from the source snapshot txg and emits compact `dmu_diff_record_t` ranges describing dnodes that are free or in use.

## Major Responsibilities

- Validates that both input names are snapshots.
- Holds the target and source datasets.
- Ensures the target snapshot is before the source snapshot according to `dsl_dataset_is_before()`.
- Traverses metadata dnode blocks modified after the source snapshot creation txg.
- Emits `DDR_FREE` and `DDR_INUSE` records to a vnode.
- Coalesces contiguous free or in-use object ranges into single records.

## Key Data

- `struct diffarg` carries:
  - output vnode,
  - output offset pointer,
  - current error,
  - current pending `dmu_diff_record_t`.

## Important Functions

- `write_record()` appends the current diff record to the output vnode unless the current record type is `DDR_NONE`.
- `report_free_dnode_range()` merges adjacent free ranges or flushes the previous record and starts a new `DDR_FREE` record.
- `report_dnode()` reports one object as free or in-use, merging adjacent in-use ranges.
- `diff_cb()` is the traverse callback:
  - Ignores non-meta-dnode blocks.
  - For holes, computes the dnode-object range covered by the hole and reports it free.
  - For level-0 dnode blocks, reads the block through ARC, optionally raw for protected blocks, walks dnode slots, and reports each object.
  - Returns `TRAVERSE_VISIT_NO_CHILDREN` for dnode leaf blocks because regular file data is irrelevant to this diff.
- `dmu_diff()` orchestrates validation, dataset holds, long hold, traversal flags, final record flush, and cleanup.

## Interactions

- Uses `traverse_dataset()` with:
  - `TRAVERSE_PRE`
  - `TRAVERSE_PREFETCH_METADATA`
  - `TRAVERSE_NO_DECRYPT`
- Uses ARC reads for dnode blocks.
- Uses vnode `vn_rdwr()` to append binary diff records.
- Uses DSL pool/dataset hold and release APIs.

## Notable Invariants

- Inputs must be snapshot names containing `@`.
- The target/source ordering check returns `EXDEV` if the requested relationship is invalid.
- Signal checks can abort traversal with `EINTR`.
- The diff intentionally reports dnode allocation state, not file data block contents.
- Encrypted datasets can be traversed without decrypting because dnode blocks are usable for this purpose, but userland may still require loaded keys for later object-stat lookup.

## Research Notes

This file is small and focused. Its behavior depends strongly on traversal semantics and the encoded layout of dnodes in the meta-dnode object. Changes to dnode sizing, large dnodes, traversal flags, or diff record format would need corresponding review here.
