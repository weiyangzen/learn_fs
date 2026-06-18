# File Research: sources/os/plan9/9front/sys/src/cmd/venti/srv/dcache.c

Implements the raw disk block cache and ordered write-behind flushing.

Key behavior:
- `initdcache` allocates fixed-size cache blocks sized to `maxblocksize`, a hash table, an LRU-ish heap, write arrays, and starts flush/delay procs.
- `_getdblock` looks up blocks by `(Part*, addr)`, loads data on miss, upgrades locks as needed, and creates per-part write threads lazily for write modes.
- `putdblock` releases block read/write lock and returns clean unreferenced blocks to the victim heap.
- `dirtydblock` marks a block with a dirty phase and schedules flushes based on dirty count.
- Victim selection uses `used2` second-most-recent timestamp in a heap.
- `flushproc` collects dirty blocks, sorts by dirty phase, partition, and address, writes each phase in order via `parallelwrites`, flushes partitions, then marks blocks clean/heapable.
- `writeproc` serializes writes for one partition and updates write stats.
- `emptydcache`, `flushdcache`, `kickdcache`, and `checkdcache` expose maintenance and invariant checks.

Interactions:
- Arena writes use dirty phase ordering to ensure data, clump-info blocks, and trailer write in safe order.
- Index writes bypass dcache dirtying and update cached copies through `_getdblock(..., load=0)` in `icachewrite.c`.

Notable details:
- File-level lock ordering rules are documented: cache lock may be taken while holding a block lock, not the reverse.
- A comment says new-block usage timestamp heuristic is “not reasonable”.
- `flushpart` errors inside `parallelwrites` are not handled beyond a comment.
