# File Research: sources/os/linux/linux/fs/xfs/scrub/bitmap.c

This file implements interval-tree backed sparse bitmaps for 64-bit and 32-bit integer spaces. The scrub/repair subsystem uses these bitmaps to track extents of filesystem blocks, AG blocks, and AG inode numbers without allocating dense bit arrays for large address spaces.

Both implementations use Linux interval tree generation macros over private node types. Each node records a start and last bit, plus the interval-tree subtree-last field. The public operations are mirrored for `xbitmap64` and `xbitmap32`: initialize, destroy, set, clear, subtract (`disunion`), count set bits (`hweight`), walk set ranges, test whether a range begins set or clear and for how long, and test emptiness. The 32-bit variant also counts the number of set regions.

`set` first clears the target range to eliminate overlapping nodes, then merges with left-adjacent and/or right-adjacent intervals when possible, otherwise allocates a new interval node. `clear` handles the four overlap cases: clearing the middle of a larger interval, trimming the left side, trimming the right side, or removing a fully covered interval. Splitting a node allocates a new right-side node, so memory allocation failure can be returned from clear/set operations.

`disunion` implements the repair pattern `bitmap &= ~sub` by walking every interval in `sub` and clearing it from `bitmap`. Many repair algorithms in this group use that to subtract still-live metadata from all blocks with a shared rmap owner, leaving likely stale blocks to reap.

Callers must not mutate a bitmap while walking it. Walk callbacks can return any nonzero value to stop iteration; `-ECANCELED` is documented as a caller-owned sentinel because the iterator itself does not generate it.
