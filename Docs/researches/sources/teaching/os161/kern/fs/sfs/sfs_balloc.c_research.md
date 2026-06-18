# File Research: sources/teaching/os161/kern/fs/sfs/sfs_balloc.c

Implements SFS block allocation over the in-memory freemap bitmap.

Key functions:
- `sfs_balloc` allocates a free bitmap bit, marks the freemap dirty, validates the block is within `sb_nblocks`, clears the newly allocated disk block, and rolls back the bitmap on clear failure.
- `sfs_bfree` unmarks a block and marks the freemap dirty.
- `sfs_bused` checks whether a block is allocated and panics on out-of-range block numbers.

Notable behavior:
- Newly allocated blocks are zeroed before being returned, which is relied on for new inode blocks and indirect blocks.
- Freemap persistence is deferred to filesystem sync.
