# File Research: sources/os/plan9/9front/sys/src/cmd/venti/srv/syncindex0.c

`syncindex0.c` implements the index synchronization algorithm. For each arena, it runs `syncarena()` with repair enabled, ignores expected header/directory-zero categories where safe, and indexes clumps present in `memstats` but not yet reflected in `diskstats`.

`syncarenaindex()` reads each new clump’s `ClumpInfo`, builds `IAddr`, updates an `AState`, and calls `insertscore()` with dirty entries. After successful insertion, `syncindex()` writes the arena tail and schedules delayed index-cache flushing.

This is the bridge from append-only arena recovery to persistent index catch-up.
