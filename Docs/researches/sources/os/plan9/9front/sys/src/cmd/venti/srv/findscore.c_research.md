# File Research: sources/os/plan9/9front/sys/src/cmd/venti/srv/findscore.c

Command-line brute-force score search across an arena partition.

Key behavior:
- Parses a Venti score string and opens an arena partition read-only.
- Initializes arenas and dcache.
- `findscore` scans each arena’s clump-info directory in chunks, compares scores, and prints clump number, type, sizes, and running data position for matches.
- Prints total occurrences.

Interactions:
- Uses `initarenapart`, `readclumpinfos`, and `strscore`.

Notable details:
- `clumpinfoeq` is defined here and also declared twice in `fns.h`.
- Has a `//ZZZ remove fprint?` comment near unconditional directory progress printing.
