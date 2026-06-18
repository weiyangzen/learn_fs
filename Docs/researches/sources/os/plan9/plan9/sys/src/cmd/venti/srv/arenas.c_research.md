# File Research: sources/os/plan9/plan9/sys/src/cmd/venti/srv/arenas.c

Purpose: manage arena partitions, arena maps, and name lookup.

Key behavior:
- Maintains a 512-bucket hash table from arena name to `Arena`.
- `addarena`, `findarena`, and `delarena` manage global lookup.
- `initarenapart` reads an arena partition header, validates block/table layout, reads the arena map, initializes each arena, checks map/name consistency, and registers arenas.
- `newarenapart` creates a new arena partition layout and writes the header.
- `wbarenapart` writes the partition header and arena map.
- `freearenapart` frees maps/arena arrays and optionally unregisters/frees arenas.
- `okamap` verifies sorted non-overlapping arena ranges within partition bounds.
- `maparenas` resolves map names to arena pointers.
- `readarenamap`, `wbarenamap`, `parseamap`, and `outputamap` implement the textual arena map format.

Integration points:
- Calls `initarena`/`freearena` from `arena.c`.
- Uses `Part`, `IFile`, zblocks, format helpers, and name validation helpers.

Risks:
- `Emergency` is a compile-time constant `0`; emergency partial-load paths are present but disabled.
- Map parsing exits early on malformed rows and must free allocated maps on failures.
- Duplicate arena names across partitions are rejected through global lookup.
