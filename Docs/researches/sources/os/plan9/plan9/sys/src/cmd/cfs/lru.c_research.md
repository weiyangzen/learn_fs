# File Research: sources/os/plan9/plan9/sys/src/cmd/cfs/lru.c

This file implements a small circular doubly-linked LRU list utility.

Key behavior:
- `lruinit()` initializes a list head.
- `lruadd()` appends a member at the list tail.
- `lruref()` moves a member to the tail, marking it most recently used.
- `lruderef()` moves a member to the head, marking it least recently used.

Important details:
- Lists are circular with the head acting as sentinel.
- The cache code embeds `Lru` as the first field in multiple structs so list nodes can be cast to container structs.

Filesystem relevance:
- Direct support utility for `cfs` block and inode cache eviction.
