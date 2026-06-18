# File Research: sources/os/plan9/plan9/sys/src/cmd/cfs/inode.h

This header defines inode-cache structures and APIs for `cfs`.

Key contents:
- `Nicache = 64`.
- `Ibuf`: LRU node, in-use flag, inode number, and cached `Inode`.
- `Imap`: LRU node, qid, backpointer to resident `Ibuf`, and in-use flag.
- `Icache`: embeds `Disk`, adds inode sizing/placement fields, fixed inode buffer array, buffer LRU head, qid map, and map LRU head.
- Prototypes for inode allocation, lookup, reading, formatting, initialization, removal, qid update, writing, freeing, and version increment.

Important details:
- `Lru` must be first in `Ibuf` and `Imap`.
- `Icache` composes disk, block cache, inode cache, and qid mapping state.

Filesystem relevance:
- Direct. Defines the metadata cache layer for `cfs`.
