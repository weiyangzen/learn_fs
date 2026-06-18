# File Research: sources/os/plan9/9front/sys/src/cmd/disk/exsort.c

Utility for sorting and reporting block-number cache files.

Key behavior:
- Reads a file of `ulong` values, defaulting to `/adm/cache`.
- Counts low/high marker bits to infer endianness; if high bits dominate, byte-swaps values.
- Sorts block numbers and reports counts per `Wormsize` disk-sized range for 100 ranges.
- With `-w`, writes the sorted data back, swapping back if needed.

Research notes:
- Appears tailored for historical WORM/cache administration.
- Reads the full file into memory.
