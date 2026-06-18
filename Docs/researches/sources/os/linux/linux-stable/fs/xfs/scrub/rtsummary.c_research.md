# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/rtsummary.c

## Purpose
Scrubs the realtime summary file by recomputing summary counters from the realtime bitmap into an xfile and comparing the computed data against the ondisk rtsummary inode.

## Major Components
- `xchk_setup_rtsummary`: allocates state and xfile, initializes rtgroup, optional repair setup, transaction, live summary inode, quota attachment, locking, and geometry.
- xfile suminfo helpers:
  - `xfsum_load`
  - `xfsum_store`
  - `xfsum_copyout`
- Computation:
  - `xchk_rtsum_record_free`
  - `xchk_rtsum_compute`
- Comparison:
  - `xchk_rtsum_compare`
- Top-level scrub: `xchk_rtsummary`.

## Control Flow and Invariants
Setup computes expected realtime geometry while bitmap/summary metadata are locked. The scrubber checks:
- `sb_rextents` matches computed rextents.
- `m_rsumlevels` and `m_rsumblocks` match computed summary geometry.
- summary inode size is fsblock-aligned and large enough.
- metadata inode forks are healthy.

It then queries all free extents from the rtbitmap. For each free extent, it computes the summary offset from bitmap block offset and length log, increments the staged suminfo word in the xfile, and later compares staged blocks to ondisk rtsummary blocks. Summary file mappings must be written and not extend past EOF.

## Dependencies and Integration
Uses realtime allocation query APIs, xfile storage, metadata inode scrub, rtgroup locking, and repair setup from the rtsummary repair path declared in `rtsummary.h`.

## Risk and Edge Cases
- If recomputation returns `-EFSCORRUPTED`, the bitmap is marked corrupt because rtsummary scrub depends on bitmap correctness.
- Supports both old and rtgroup suminfo raw formats via `xchk_rtsum_inc`.
- Allows summary file to be larger than current required size because growfsrt expands files before updating geometry.
