# File Research: sources/os/linux/linux-stable/fs/ufs/balloc.c

## Summary
Implements UFS fragment and block allocation/freeing, cylinder-group bitmap searches, fragment extension, block relocation for tail growth, and 4.4BSD cluster accounting.

## Main Responsibilities
- Frees partial fragments and whole blocks while updating cylinder group, summary, fragment, and cluster counters.
- Allocates new fragments for direct and indirect block mapping.
- Extends existing tail fragments when possible.
- Allocates replacement blocks and updates page-cache buffer mappings when a tail must move.
- Searches preferred, quadratically rehashed, and linearly scanned cylinder groups for space.
- Uses bitmap scan tables for fragment availability patterns.
- Tracks contiguous free-block clusters for 4.4BSD-style cylinder groups.

## Important Behavior
`ufs_new_fragments()` handles three cases: allocate a new fragment run, extend an existing fragment run in place, or allocate a new block/run and move existing tail data.

`try_add_frags()` protects against `i_blocks` overflow before accounting allocated fragments.

## Risks
Allocator correctness depends on `s_lock`, cylinder-group cache consistency, bitmap bit polarity, summary counters, and inode byte accounting all staying synchronized. Moving tail blocks requires updating page-cache buffer block numbers without losing dirty data.
