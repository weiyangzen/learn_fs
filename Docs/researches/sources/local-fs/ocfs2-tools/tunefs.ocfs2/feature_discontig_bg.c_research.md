# File Research: sources/local-fs/ocfs2-tools/tunefs.ocfs2/feature_discontig_bg.c

## Purpose
Enables or disables discontiguous block group support.

## Main Behavior
- `enable_discontig_bg()` is a superblock incompat flag set after prompt.
- Disable path is more restrictive:
  - Scans every inode allocator and extent allocator chain for every slot.
  - `check_discontig_bg()` reads each group descriptor.
  - If any descriptor is actually discontiguous, disable aborts.
  - If a non-discontiguous descriptor uses the newer `bg_size`, records it for later conversion.
  - `change_bg_size()` rewrites recorded group descriptors back to old-style bitmap size.
  - Clears `OCFS2_FEATURE_INCOMPAT_DISCONTIG_BG` and writes the superblock.
- Defines `discontig_bg_feature` with `TUNEFS_FLAG_RW | TUNEFS_FLAG_ALLOCATION | TUNEFS_FLAG_LARGECACHE`.

## Dependencies
- OCFS2 chain iteration, group descriptor read/write, and bitmap-size helpers.
- Tunefs allocator checks and large cache support.

## Notes
Disabling is only possible when no actual discontiguous block groups exist. The code can normalize compatible group descriptors but will not migrate truly discontiguous allocation groups.
