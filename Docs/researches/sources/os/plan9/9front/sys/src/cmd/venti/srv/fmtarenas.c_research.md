# File Research: sources/os/plan9/9front/sys/src/cmd/venti/srv/fmtarenas.c

Formats an arena partition and creates evenly spaced arenas.

Key behavior:
- CLI: `fmtarenas [-Z] [-b blocksize] [-a arenasize] name file`, plus `-4` for old arena version and `-D` trace.
- Defaults: 8 KiB block size, 512 MiB arena size, 512 KiB arena table, arena version 5.
- Optionally zeroes the partition.
- Creates a new `ArenaPart`, calculates number of arenas from available partition size and `MinArenaSize`, creates each arena with name template plus index, fills `AMap`, then writes the arena partition header/table.

Interactions:
- Uses `newarenapart`, `newarena`, `wbarenapart`, dcache.

Notable details:
- Comment notes table size should be determined from number of arenas instead of fixed 512 KiB.
