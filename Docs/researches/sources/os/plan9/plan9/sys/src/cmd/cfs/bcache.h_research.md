# File Research: sources/os/plan9/plan9/sys/src/cmd/cfs/bcache.h

This header defines the `cfs` block-cache structures and APIs.

Key contents:
- `Nbcache = 32` fixed buffer count.
- `Bbuf`: LRU node, block number, in-use flag, dirty-list link, dirty flag, and data pointer.
- `Bcache`: LRU head, block size, disk fd, dirty-list head/tail, and fixed buffer array.
- Prototypes for block-cache initialization, allocation, reads, dirty marking, writes, sync, raw block I/O, and error/warning helpers.

Important details:
- `Lru` must be first in `Bbuf` and `Bcache`, allowing casts between list nodes and containing objects.

Filesystem relevance:
- Direct. Defines the low-level cache used by the `cfs` filesystem cache.
