# File Research: sources/os/plan9/plan9/sys/src/cmd/venti/srv/fmtarenas.c

Implements `fmtarenas`, which formats an arena partition. It accepts a name template and file, with options for arena size, block size, version 4 output, and zeroing.

The command opens the target part, optionally zeros it, initializes disk cache, creates a new `ArenaPart`, divides available space from `arenabase` into arena-sized ranges, creates each arena with `newarena()`, fills the arena map, and writes the arena partition header/table with `wbarenapart()`.

Defaults are 8 KiB blocks, 512 MiB arenas, 512 KiB arena table, and Arena version 5. Version 4 defaults to zeroing for older format expectations.
