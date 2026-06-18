# File Research: sources/os/plan9/plan9/sys/src/cmd/venti/srv/syncindex0.c

Purpose: Core index synchronization logic used by the server and `syncindex` tool.

Key behavior:
- `syncindex` calls `syncarena` for each arena, tolerates header and clump-info zero/directory repairs as configured, then indexes newly discovered clumps.
- `syncarenaindex` reads clump info from the arena’s diskstats position to memstats position, constructs `IAddr`, inserts scores into the index, and advances arena stats.
- Writes updated arena metadata with `wbarena` and triggers delayed index-cache writeback.

Dependencies:
- Uses arena sync, clump info reading, score insertion, disk cache, index cache, and arena writeback.

Notable details:
- Corrupt clumps are not explicitly skipped here; indexing follows directory entries returned by `readclumpinfo`.
