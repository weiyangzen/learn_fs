# File Research: sources/os/plan9/plan9/sys/src/cmd/venti/srv/unittoull.c

Purpose: Parses unsigned integer strings with storage-size suffixes.

Key behavior:
- Accepts plain numeric strings plus `k`, `m`, `g`, or `t` suffixes.
- Returns all-ones `TWID64` on nil input or invalid trailing characters.

Dependencies:
- Uses Plan 9 integer types from `stdinc.h`.

Notable details:
- Parses the base number with `strtoul`, so very large inputs depend on host `ulong` width before suffix multiplication.
