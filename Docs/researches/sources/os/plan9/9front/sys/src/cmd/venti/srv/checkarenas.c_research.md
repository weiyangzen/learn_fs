# File Research: sources/os/plan9/9front/sys/src/cmd/venti/srv/checkarenas.c

Command-line arena header consistency checker and optional fixer.

Key behavior:
- `checkarena` optionally resets in-memory stats for a full scan, repeatedly calls `syncarena`, compares recomputed `memstats` with old values, and reports incorrect arena header fields.
- With `-f`, writes corrected arena header fields by copying `memstats` to `diskstats`, calling `wbarena`, and flushing dcache.
- `-a` enables full scan/recompute mode.
- `-v` prints arena details and progress.
- Optional arena-name arguments restrict which arenas are checked.

Interactions:
- Uses `initarenapart`, `syncarena`, `printarena`, `wbarena`, and dcache.
- Opens the arena partition read-only unless fixing.

Notable details:
- `syncarena` is called repeatedly while it reports `SyncHeader`, allowing progressive header repair/checking.
