# File Research: sources/os/plan9/9front/sys/src/cmd/sam/disk.c

`disk.c` provides sam's temporary storage allocator for buffer blocks. It creates an ORCLOSE temp file under `/tmp` and assigns byte offsets within that file to `Block` descriptors.

Blocks are bucketed by rounded size using `Blockincr`, with `Maxblock` as the largest supported block. `ntosize` maps a rune count to an allocation size and free-list bucket.

`disknewblock` reuses a block from the right free list or allocates `Block` descriptors in chunks of 100. New disk space is append-only within the temp file and checked for address overflow.

`diskrelease` returns a block to the appropriate free list. `diskwrite` rewrites a block in place if the rounded size is unchanged or reallocates a block if the size class changed. `diskread` validates the requested size and reads runes from the block's temp-file address.
