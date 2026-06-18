# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/flashfs/journal.c

This file implements flashfs's flash journal loading, recovery, allocation, and compaction.

Key behavior:
- Scans sectors into two generations and a free-sector list.
- Replays journal records into the in-memory entry tree and extent lists.
- Recovers several interrupted-write "window" cases by freeing duplicates, duplicating sectors, or adjusting generations.
- Allocates new sectors and appends journal records safely.
- Summarizes old generation data into the current generation to reclaim sectors.
- Computes write space needs and switches to read-only on generation exhaustion.

Important details:
- Sector headers store magic, generation number, and sequence number with compact integers.
- Record append writes payload first and commits by writing the type byte.
- Time deltas are stored relative to sector time; `now()` manages clock rollback by applying `delta`.
- Summary records preserve live metadata and extents while freeing old sectors.
- `maxwrite` is bounded by sector size and `WRSIZE`.

Filesystem relevance:
- Direct: persistence, crash recovery, and garbage collection engine for flashfs.
