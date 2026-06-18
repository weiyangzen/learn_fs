# File Research: sources/os/plan9/9front/sys/src/cmd/cfs/bcache.h

Block-cache structures and declarations for `cfs`.

Key definitions:
- `Nbcache` is 32 cached disk blocks.
- `Bbuf` embeds `Lru`, block number, in-use flag, dirty-list link, dirty flag, and data pointer.
- `Bcache` embeds `Lru`, block size, disk fd, dirty-list head/tail, and fixed `Bbuf` array.
- Declares cache init/read/write/mark/sync APIs and main-program error hooks.

Dependencies:
- Requires `Lru` and on-disk block constants.

Research notes:
- `Lru` must be first in `Bbuf` because list routines cast entries through embedded list nodes.
