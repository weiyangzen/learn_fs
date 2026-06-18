# File Research: sources/os/plan9/9front/sys/src/cmd/venti/srv/lump.c

`lump.c` is the main Venti read/write data path for content-addressed blocks. `readlump()` handles zero-score reads, checks the lump cache, looks up index entries, loads arena clumps, validates size/type/score, and inserts successful reads back into the cache.

`writelump()` hashes incoming packet data, suppresses empty/dev-null writes, detects cache duplicates and SHA1 collisions, optionally queues writes, and delegates actual storage to `writeqlump()`. Duplicate writes can either trust the index or verify by re-reading existing data when `verifywrites` is enabled.

The file couples the RPC layer, lump cache, index lookup, arena clump loading, write queue, and cache/disk flush policy. Correctness hinges on score verification in `readilump()` and duplicate-data comparison before accepting an existing score.
