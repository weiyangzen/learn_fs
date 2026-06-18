# File Research: sources/os/bsd/netbsd-src/sys/ufs/lfs/lfs_rfw.c

## Purpose

`lfs_rfw.c` implements LFS roll-forward recovery. After an unclean mount, it validates partial segments written after the last checkpoint and reconstructs newer inode generations, inode metadata, and direct data block mappings before forcing a clean checkpoint.

## Main Responsibilities

- Allocates or replaces specific inode generations during recovery with `lfs_rf_valloc()`.
- Updates block metadata and segment accounting for recovered data blocks with `update_meta()`.
- Copies dinode metadata while intentionally excluding block pointers and block counts via `update_inoblk_copy_dinode()`.
- Scans inode blocks to discover highest generation numbers with `update_inogen()`.
- Replays inode blocks with `update_inoblk()`.
- Replays FINFO data-block mappings with `finfo_func_rfw()`.
- Parses and validates partial segments through `lfs_parse_pseg()`.
- Coordinates the four roll-forward phases in `lfs_roll_forward()`.
- Drops pages from recovered vnodes after replay to reset VM state.

## Partial Segment Parser

`lfs_parse_pseg()` skips label/superblock padding, reads the segment summary, validates magic, optional summary checksum, serial/identity or timestamp constraints, and expected serial sequencing. It walks interleaved inode blocks and FINFO-described file blocks, either validating data checksums or invoking supplied inode/FINFO callbacks. It advances to the next partial segment according to the summary's `next` pointer when the current segment lacks room for another partial segment, matching `LFS_PARTIAL_FITS` in `lfs_segment.c`.

The same parser is reused by the cleaner, emptiness checker, and roll-forward code.

## Roll-Forward Phases

`lfs_roll_forward()` skips clean filesystems, disabled recovery, v1 filesystems, and missing process context. For v2+ dirty filesystems:

1. Validates successive partial segments after the checkpoint using checksums and serial numbers, marking covered segments dirty and remembering the last complete non-continuation partial segment.
2. Sets the filesystem write offset to the end of the replay range and chooses a clean next segment so replay does not overwrite data being recovered.
3. Scans inode blocks to record highest inode generations in the Ifile.
4. Replays inode blocks for current generations, updating inode addresses and dinode metadata.
5. Replays FINFO data block mappings, calling `lfs_update_single()` and adding segment bytes for recovered blocks.
6. Writes a synchronous checkpoint and resets availability/accounting from on-disk segment state.

## Recovery Semantics

`lfs_rf_valloc()` can reuse an already-cached matching generation, replace an older cached generation with a newer dinode, or create a new vnode from dinode metadata. Data blocks are not copied during replay; they already exist in the post-checkpoint log, so recovery updates metadata to point at them. Short symlink payloads are copied from dinode direct-block storage.

## Safety Notes

Roll-forward for v1 filesystems is disabled because timestamp-based partial-segment ordering can be fooled by clock rollback. v2+ uses monotonically increasing serial numbers and filesystem identifiers. Incomplete DIROP continuation chains are discarded by replaying only through the last complete non-`SS_CONT` boundary.
