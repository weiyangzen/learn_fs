# File Research: sources/local-fs/xfsprogs/repair/dino_chunks.c

## Purpose

`dino_chunks.c` validates, discovers, and processes inode allocation chunks during `xfs_repair`. It checks inode blocks, reconstructs missing inode chunk records when possible, processes known and uncertain inode records, updates incore block-state maps, handles sparse inode clusters, and records inode state needed by later repair phases.

## Main Responsibilities

- Validate candidate inode blocks with basic dinode checks.
- Verify whether an uncertain inode belongs to a valid inode chunk.
- Add verified missing inode chunks to the good inode tree.
- Mark inode blocks in the incore block map.
- Process every inode in a known chunk through `process_dinode`.
- Correct inode allocation map state when disk inode state disagrees.
- Handle sparse inode clusters and optionally punch all-bad sparse clusters.
- Track directory status, parent inode numbers, file type, and on-disk nlink count.
- Mark special filesystem inodes as needing reconstruction if they are cleared.

## Key Functions

- `check_aginode_block` reads one filesystem block and counts dinodes that pass uncertain verification.
- `verify_inode_chunk` tries to establish a valid chunk around a candidate inode and inserts a good inode record if successful.
- `verify_aginode_chunk` and `verify_aginode_chunk_irec` are AG-relative wrappers.
- `process_inode_agbno_state` updates the incore block map for an inode block.
- `process_inode_chunk` reads cluster buffers and processes all inodes covered by one allocation unit.
- `process_aginodes` walks the known good inode tree for an AG.
- `check_uncertain_aginodes` validates uncertain records before normal processing.
- `process_uncertain_aginodes` validates and immediately processes uncertain records discovered after the main AG pass.

## Inode Chunk Discovery

`verify_inode_chunk` has three major cases:

- Filesystems with multiple chunks per block (`ialloc_blks == 1`) validate the block directly and create records for all chunks in the block.
- Aligned inode filesystems round down to the inode alignment and validate the full aligned allocation.
- Older unaligned filesystems search around the candidate block, use nearby known inode records to tighten the range, scan outward until non-inode blocks are found, and accept a chunk-sized valid range if it does not conflict with allocated data.

When accepted, the code creates an inode record, marks all inodes free by default, marks the discovered inode used, and marks backing blocks as `XR_E_INO`.

## Inode Processing Flow

`process_inode_chunk` reads all cluster buffers for the chunk unless a cluster is sparse. In discovery mode, it first verifies whether enough dinodes are valid to keep the chunk; if no valid inodes are found, the caller can delete the records.

For each present inode, it calls `process_dinode`, updates dirty buffers and CRCs, reconciles free/in-use state in the incore inode record, stores file type and nlink count, tracks directory parent information, and handles cleared special inodes.

Sparse cluster inconsistencies are handled by marking affected inodes sparse and free if the imap claims present inodes inside a skipped sparse cluster.

## Special Inode Handling

If a cleared inode is one of the root, metadata directory, realtime bitmap, realtime summary, rtgroup bitmap, rtgroup summary, rtgroup rmap, or rtgroup refcount inodes, the code sets global flags so later phases can rebuild or avoid dependent checks.

## Dependencies

This file depends on:

- AVL-backed inode record trees from repair incore state.
- AG block-state bitmap helpers.
- dinode verification and processing from `dinode.h`/related repair code.
- prefetch/progress coordination.
- sparse inode geometry and libxfs inode buffer verifiers.
- realtime and rmap/refcount repair state helpers.

## Important Invariants

- Inode chunks must align to `XFS_INODES_PER_CHUNK`.
- Multi-chunk-per-block filesystems may require synthesizing missing chunk records to cover a full inode allocation.
- Blocks already claimed by file data or metadata conflicts are marked multiply claimed unless metadata-directory reconstruction makes overlap tolerable.
- Sparse inodes occur at cluster granularity for the handled punching path.
- Dirty dinodes have CRCs recalculated before buffers are released.
- Uncertain inode trees are destroyed as they are checked/processed.

## Repair and Risk Notes

This file is a core phase-3/phase-4 repair bridge: it turns uncertain references into inode records, processes actual dinodes, and feeds later directory/link-count phases. The hardest logic is unaligned legacy chunk discovery and the interaction between sparse clusters, missing inobt records, and avoiding data loss from falsely claiming user data as inode chunks.
