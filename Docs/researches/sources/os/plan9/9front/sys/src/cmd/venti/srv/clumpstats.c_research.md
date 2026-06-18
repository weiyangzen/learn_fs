# File Research: sources/os/plan9/9front/sys/src/cmd/venti/srv/clumpstats.c

Command-line utility producing a histogram of clump sizes by Venti type.

Key behavior:
- Global `count[VtMaxLumpSize][VtMaxType]` stores frequency by uncompressed size and type.
- `readarenainfo` reads clump-info directories in 32K-entry chunks, validates type/size range, and increments counts.
- `clumpstats` iterates all arenas in the main index, totals clumps, and prints rows for nonzero sizes.
- Supports `-B blockcachesize`.

Interactions:
- Initializes Venti config, dcache, and uses `readclumpinfos`.

Notable details:
- Bad clump metadata is printed and skipped rather than aborting immediately.
