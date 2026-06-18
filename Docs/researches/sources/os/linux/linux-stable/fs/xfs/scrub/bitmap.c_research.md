# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/bitmap.c

## Purpose
Implements sparse interval bitmaps for scrub and repair using Linux generic interval trees. It provides nearly identical 64-bit and 32-bit variants for filesystem block and per-AG/block/inode index use cases.

## Main APIs
For `xbitmap64`:
- `xbitmap64_init`, `xbitmap64_destroy`
- `xbitmap64_set`, `xbitmap64_clear`
- `xbitmap64_disunion`
- `xbitmap64_hweight`
- `xbitmap64_walk`
- `xbitmap64_empty`
- `xbitmap64_test`

For `xbitmap32`:
- `xbitmap32_init`, `xbitmap32_destroy`
- `xbitmap32_set`, `xbitmap32_clear`
- `xbitmap32_disunion`
- `xbitmap32_hweight`
- `xbitmap32_walk`
- `xbitmap32_empty`
- `xbitmap32_test`
- `xbitmap32_count_set_regions`

## Key Behavior
Each set region is an interval-tree node with start and inclusive last bit. `set` first clears overlap, then merges with left/right adjacent intervals or creates a new interval. `clear` handles four cases: split interval, trim left overlap, trim right overlap, or remove fully covered intervals. `disunion` applies logical `bitmap &= ~sub` by clearing every interval from `sub`.

`test` reports whether a requested start point is set and adjusts the supplied length to the contiguous set or clear run length before the next transition.

## Dependencies and Interactions
Used by many scrub repair modules to track sparse sets of blocks, AG blocks, fsblocks, and aginos via typed wrappers. Allocation uses `XCHK_GFP_FLAGS`.

## Failure Handling
Only interval split/set allocation can return `-ENOMEM`. Walk callbacks can stop iteration with any nonzero code; `-ECANCELED` is reserved by convention for intentional early stop.
