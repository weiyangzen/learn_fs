# File Research: sources/os/bsd/netbsd-src/sys/ufs/lfs/lfs_kclean.c

## Purpose

`lfs_kclean.c` implements the in-kernel LFS cleaner. It selects dirty segments, pre-references live inodes, rewrites live inode/data blocks into the log, checks segment emptiness, runs an autoclean daemon, and exposes control over cleaner policy.

## Main Responsibilities

- Parses partial segments using callbacks shared with roll-forward code.
- Marks live inodes as being cleaned with `lfs_setclean()`.
- Rewrites current live blocks from old segments via `rewrite_block()` and `lfs_bwrite_ext(..., BW_CLEAN)`.
- Rewrites whole segments through `lfs_rewrite_segment()` and batches through `lfs_rewrite_segments()`.
- Checks whether a segment still contains live inode or file blocks with `lfs_checkempty()`.
- Selects candidate segments using greedy free-space benefit or Rosenblum-style cost-benefit age weighting.
- Runs `lfs_cleanerd()` over mounted LFS instances that have autoclean enabled.
- Rewrites whole files for coalescing/testing via `lfs_rewrite_file()`.
- Enables/disables and configures autoclean mode via `lfs_cleanctl()`.

## Segment Rewrite Flow

`lfs_rewrite_segments()` first enters the writer path and cleaner lock to prevent new directory operations and conflicting cleaners. Before taking the segment lock, it walks candidate partial segments and calls `ino_func_setclean()` and `finfo_func_setclean()` to identify live vnodes safely. It then takes `SEGM_CLEAN`, revalidates that candidate segments are dirty and not active, rewrites each live block/inode, flushes the generated segment with `lfs_writeseg()`, records direct-fragment and written-offset counts, and releases locks.

`finfo_func_rewrite()` validates inode number and generation, rejects unavailable or `VU_DIROP` vnodes, marks the vnode cleanable, reads blocks only if their current bmap address still matches the parsed old offset, writes replacement buffers into the current segment, updates metadata, and writes the inode. `ino_func_rewrite()` handles inode blocks not already covered by data-block rewrite.

## Autoclean Policy

`clean()` computes a priority threshold from configured parameters, filesystem pressure, `LFS_MUSTCLEAN`, and available/free block ratios. It scans every segment, skipping active, already-clean, ready, empty, zero-byte, and error segments. The highest-priority dirty segment above threshold is rewritten; repeated failure on the same segment marks it `SEGUSE_ERROR`. Under severe pressure it forces double checkpoints to reclaim ready/empty segments.

`lfs_cleanctl()` installs one of three modes: off, greedy, or cost-benefit. It creates the global `lfs_cleaner` kernel thread on first enabled filesystem and coordinates shutdown status with `lfs_cleanquitcv`.

## Concurrency Notes

The cleaner carefully separates pre-reference work from segment-locked rewrite work to avoid vnode/cleaner deadlocks. It refuses active segments, avoids `VU_DIROP` relocation, uses `LK_NOWAIT` vnode acquisition, and only rewrites inodes found on the clean list when necessary. `lfs_cleanerd()` holds an extra VFS ops reference while running so the LFS module cannot unload underneath the daemon.
