# File Research: sources/os/plan9/9front/sys/src/cmd/cfs/lru.c

Circular doubly linked LRU list implementation.

Key behavior:
- `lruinit` initializes a list head pointing to itself.
- `lruadd` inserts a member before the head’s current first entry.
- `lruref` moves a member to the most-recent position unless it is already there.
- `lruderef` moves a member to the least-recent position.

Dependencies:
- Includes `lru.h`.

Research notes:
- `Bbuf`, `Ibuf`, and `Imap` embed `Lru` as their first field so these generic routines can operate on them.
