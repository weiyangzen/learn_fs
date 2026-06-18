# File Research: sources/os/plan9/plan9/sys/src/cmd/venti/srv/syncarena.c

Purpose: Synchronizes an arena’s in-memory/directory metadata with clumps found on disk.

Key behavior:
- `syncarena` scans clumps from the arena’s current `memstats.used`, validates clump magic, loads clumps, verifies scores/types, compares directory `ClumpInfo`, and updates `memstats`.
- Can mark broken clumps as `VtCorruptType` and rewrite clump headers/directories when `fix` is enabled.
- Reports header/directory/data/fix flags to callers.
- `writeclumphead` and `writeclumpmagic` perform targeted arena repair writes.

Dependencies:
- Uses arena clump loading, score computation, clump info reads/writes, disk cache flushing, and sync error flags.

Notable details:
- Treats a mismatched score in an uncompressed clump as likely partial write and stops rather than repairing through it.
