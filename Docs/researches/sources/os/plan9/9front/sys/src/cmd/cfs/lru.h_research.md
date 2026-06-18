# File Research: sources/os/plan9/9front/sys/src/cmd/cfs/lru.h

LRU list node definition and API declarations.

Key definitions:
- `Lru` contains previous and next pointers.
- `Lruhead` is typedef’d to the same structure shape.

Key declarations:
- `lruinit`, `lruadd`, `lruref`, and `lruderef`.

Dependencies:
- Used by block-cache and inode-cache structures.

Research notes:
- This is an intrusive list; callers are responsible for embedding it correctly.
