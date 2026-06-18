# File Research: sources/os/linux/linux/fs/xfs/scrub/rtbitmap_repair.c

## Purpose
Repairs realtime bitmap file contents and geometry by reconstructing free-space bits from the realtime rmapbt, staging replacement file contents in an xfile and temporary inode, exchanging mappings, and reaping old blocks.

## Major Components
- `xrep_setup_rtbitmap`: creates temporary file and xfile, estimates transaction reservation.
- xfile bitmap helpers:
  - `xfbmp_load`
  - `xfbmp_store`
  - `xfbmp_copyin`
  - `xfbmp_copyout`
  - `xrep_rtbitmap_or`
- Free-space reconstruction:
  - `xrep_rtbitmap_mark_free`
  - `xrep_rtbitmap_walk_rtrmap`
  - `xrep_rtbitmap_find_freespace`
- Output preparation:
  - `xrep_rtbitmap_prep_buf`
  - `xrep_rtbitmap_data_mappings`
  - `xrep_rtbitmap_geometry`
- Top-level repair: `xrep_rtbitmap`.

## Control Flow and Invariants
Repair requires rtrmapbt and atomic exchange-range support. It:
- Fixes metadata inode forks.
- Ensures the bitmap file’s data mappings are real written extents, converting unwritten extents with zeroing when necessary.
- Repairs superblock geometry and bitmap inode size.
- Flushes busy extents before reuse.
- Walks rtrmapbt records and marks gaps between owned regions as free in an xfile bitmap.
- Verifies free gaps are rt extent aligned, valid, and neither shared nor CoW staging.
- Preallocates a temporary file, copies staged bitmap blocks into it with proper rtbitmap buffer headers, exchanges contents with the real bitmap inode, then reaps old bitmap blocks from the temp inode.

## Dependencies and Integration
Uses:
- `xfile` for staged bitmap contents.
- temporary file/exchange helpers from scrub repair.
- rtrmapbt as source of truth for used realtime extents.
- rtrefcountbt to reject shared/CoW extents from being marked free.
- `xrep_metadata_inode_forks`, `xrep_defer_finish`, and `xrep_reap_ifork`.

## Risk and Edge Cases
- Impossibly large bitmap block counts return without attempting unsafe repair.
- The code cannot use `xfs_exchmaps_estimate` because replacement extent count is unknown before reconstruction.
- Free ranges must align to realtime extent boundaries; misalignment is corruption.
- Zoned filesystems alter used-space checking elsewhere, but reconstruction still depends on rtrmapbt ownership.
