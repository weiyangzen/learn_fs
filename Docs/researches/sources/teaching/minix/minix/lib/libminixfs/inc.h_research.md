# File Research: sources/teaching/minix/minix/lib/libminixfs/inc.h

Small internal header for `libminixfs`.

Declared functions:
- `lmfs_get_partial_block`
- `lmfs_readahead`
- `lmfs_readahead_limit`

It exposes cache internals needed by `bio.c` without making them part of a broader public header.
