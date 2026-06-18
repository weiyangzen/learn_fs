# File Research: sources/os/plan9/plan9/sys/src/cmd/venti/srv/printarenas.c

Purpose: Dumps clump-derived index entries from arenas in a configured Venti index.

Key behavior:
- Loads Venti configuration, initializes disk cache, and iterates selected or all arenas.
- `dumparena` reads clump directory entries in chunks, converts each `ClumpInfo` into an `IEntry`, and prints address, score, type, and size.
- Uses the index arena map to compute logical addresses.

Dependencies:
- Uses `initventi`, `readclumpinfos`, `IEntry`, `Biobuf`, and Venti formatting.

Notable details:
- The `nskip` variable is initialized but not used to filter corrupt clumps in this utility.
