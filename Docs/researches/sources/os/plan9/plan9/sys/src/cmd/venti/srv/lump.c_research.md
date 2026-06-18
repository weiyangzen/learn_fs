# File Research: sources/os/plan9/plan9/sys/src/cmd/venti/srv/lump.c

Purpose: Implements Venti score-addressed lump read/write operations for the server.

Key behavior:
- `readlump` returns an empty packet for the zero score, checks the lump cache first, then looks up the score in the index and reads the clump from its arena.
- `writelump` computes the SHA1 score, ignores empty or configured dev-null writes, detects cached duplicate data, and either queues or directly writes the lump.
- `writeqlump` handles duplicate-on-disk checks, optional write verification, stores new clumps with `storeclump`, inserts successful writes into the lump cache, and optionally flushes caches synchronously.
- `readilump` maps an index address to an arena, loads the clump, verifies size/type/score consistency, converts the zblock to a packet, and populates the cache.

Dependencies:
- Uses packet APIs, index lookup/store, arena load, score utilities, cache APIs, statistics, tracing, and global flags from the Venti server.

Notable details:
- Duplicate writes can be treated as success without disk read unless `verifywrites` is enabled.
- Error handling distinguishes missing scores, too-small reads, index/clump mismatch, score mismatch, and possible SHA1 collisions.
