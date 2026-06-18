# File Research: sources/os/plan9/9front/sys/src/cmd/venti/srv/bloom.c

Implements the optional on-disk/in-memory Bloom filter used to avoid index lookups for definitely absent scores.

Key behavior:
- `bloominit` initializes size, default hash count, optional packed header parsing, bitmask, and data pointer.
- `readbloom` reads the first 512 bytes to parse the header, then bumps partition block size up to as much as 1 MiB for large Bloom I/O.
- `resetbloom` allocates a zeroed in-memory filter and updates bit-count stats.
- `loadbloom` reads the whole filter, counts set bits, and updates Bloom stats.
- `writebloom` packs the header into `b->data`, writes the whole filter to its partition, and flushes.
- `gethashes` derives up to 32 hash positions from a score using double-hashing style `a + b*i`, reserving header bits.
- `markbloomfilter` and `inbloomfilter` protect access with `RWLock lk`; marking also uses `QLock mod`.
- `startbloomproc` launches a background writer that waits on `writechan`, writes the filter, and signals completion.

Interactions:
- `icache.c` marks Bloom entries on dirty score insertion.
- `buildindex.c` can rebuild Bloom from arenas.
- `checkindex.c` compares/fixes Bloom contents.
- Packed header format is in `conv.c`.

Notable details:
- If Bloom is nil, unloaded, or `ignorebloom` is set, lookup returns “possibly present” to preserve correctness.
- `MaxBloomSize` has a special stat path because `size*8` can overflow `ulong`.
