# File Research: sources/os/plan9/plan9/sys/src/cmd/venti/srv/sortientry.c

Purpose: Builds a sorted temporary file of index entries derived from all arena clump directories.

Key behavior:
- `sortrawientries` initializes 256 external sort buckets, scans all arenas, fills a bloom filter, and sorts bucket contents into final index-entry order.
- `readarenainfo` reads `ClumpInfo` records in large chunks, converts them to `IEntry`, skips corrupt clumps from the sorted set, and marks bloom bits.
- `sprayientry` hashes each score into an in-memory bucket and flushes full buckets to chained chunks on disk.
- `sortiebucks` flushes buckets, allocates a final per-bucket buffer, reads chained bucket chunks, `qsort`s entries, and writes sorted entries to the temp partition.

Dependencies:
- Uses arena clump directories, `IEntry` pack/unpack, `hashbits`, `ientrycmp`, bloom filter marking, and partition I/O.

Notable details:
- Contains a debug `xabort()` path on bucket write failure.
- `freeiebucks` frees `ib->buf`, while the original allocation pointer is `ib->xbuf`; later sorting also reassigns `ib->buf`. This is a maintenance hazard in the allocator ownership model.
