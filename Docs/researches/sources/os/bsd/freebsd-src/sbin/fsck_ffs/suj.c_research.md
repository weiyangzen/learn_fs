# File Research: sources/os/bsd/freebsd-src/sbin/fsck_ffs/suj.c

## Purpose

Implements `fsck_ffs` recovery using UFS/FFS Soft Updates Journaling (SU+J). The file parses the `.sujournal` inode, reconstructs valid journal segments, builds per-cylinder-group recovery tables, and applies block, inode, truncate, link-count, and unlinked-inode repairs before marking the filesystem clean.

## Main Entry Points

- `suj_check(const char *filesys)`: top-level SU+J recovery orchestration.
- `suj_checkblkavail(ufs2_daddr_t blkno, long frags)`: checks and reserves free fragments for snapshot handling.
- `initsuj(void)`: resets all module-global recovery state.

## Core Data Structures

- `struct suj_seg`: in-memory journal segment with `jsegrec` header and copied segment bytes.
- `struct suj_rec`: wrapper for journal records queued on inode/block lists.
- `struct suj_ino`: per-inode recovery state, including ref records, move records, pending truncation, link adjustments, dot-link count, and block-adjust flag.
- `struct suj_blk`: per-base-block journal state for allocation/free records.
- `struct suj_cg`: per-cylinder-group hash tables for affected inodes and blocks, plus cached CG buffer.
- `struct jblocks` / `struct jextent`: extent map of the journal inode so the circular journal can be scanned as contiguous disk ranges.

## Recovery Flow

1. `suj_check()` initializes state, finds the journal inode in the root directory, verifies its flags, mode, size, timestamp, and link count with `suj_verifyino()`.
2. The journal inode’s block map is visited with `ino_visit()` and stored in `suj_jblocks`.
3. `suj_read()` scans journal extents, validating segment headers, timestamps, segment sizes, block continuity, and sequence metadata.
4. `suj_prune()` discards expired or non-contiguous segments and computes processed byte/record counters.
5. `suj_build()` dispatches journal records:
   - reference records to `ino_append()`
   - block records to `blk_build()`
   - truncate/sync records to `ino_build_trunc()`
6. Per-CG passes run in a strict order:
   - `cg_build()` normalizes moved and duplicate inode references.
   - `ino_unlinked()` reclaims inodes from `fs_sujfree`.
   - `cg_trunc()` applies truncates before directory lookup.
   - `cg_check_blk()` frees incomplete or orphaned block allocations.
   - `cg_adj_blk()` recalculates inode block counts.
   - `cg_check_ino()` fixes link counts and reclaims dead inodes.
7. Snapshot block counts are checked, snapshots flushed, summary totals recomputed, clean flags set, and `ckfini(1)` finalizes writes.

## Important Algorithms

- Block safety:
  - `blk_freemask()` determines whether fragments were reallocated before freeing.
  - `blk_isindir()` decides if an indirect block can be trusted and traversed.
  - `blk_free_lbn()` recursively frees indirect trees only when safe.
- Inode traversal:
  - `ino_visit()` walks UFS direct blocks, indirect blocks, and UFS2 extattr blocks.
  - `indir_visit()` recursively traverses indirect trees with trust flags.
- Directory/link recovery:
  - `ino_isat()` validates that a directory entry still points at an inode and reports dot/dotdot status.
  - `ino_clrat()` clears stale directory entries.
  - `ino_check()` computes new link counts from initial journal link count, surviving references, removals, and dot links.
  - `ino_adjust()` writes corrected counts or reclaims the inode.
- Truncation:
  - `ino_trunc()` frees full blocks beyond a target size, truncates indirect trees, updates `di_blocks`/`di_size`, and zeroes trailing bytes.
  - `indir_trunc()` clears indirect entries beyond the retained logical block.

## Integration Points

Uses `fsck_ffs` globals and helpers from `fsck.h`, including `sblock`, `ginode()`, `irelse()`, `getdatablk()`, `dirty()`, `cglookup()`, `cgdirty()`, `ckinode()`, `findino()`, `snapremove()`, `snapflush()`, `check_blkcnt()`, and `ckfini()`. It depends heavily on UFS/FFS layout macros from `<ufs/ufs/*>` and `<ufs/ffs/fs.h>`.

## Error Handling

Fatal SU+J inconsistencies call `err_suj()`, which prints context and `longjmp`s to `suj_check()`. The caller can fall back to full fsck unless declined. Direct logic errors sometimes use `errx(1)` when continued recovery would be unsafe.

## Risk Notes

This file edits live filesystem metadata directly. Correctness depends on record ordering, fragment overlap detection, sequence pruning, and not trusting reallocated indirect blocks. The most delicate areas are `blk_freemask()`, `ino_build_ref()` move/duplicate handling, truncate ordering before directory traversal, and the distinction between recoverable journal inconsistency and unrecoverable metadata corruption.
