# File Research: sources/os/plan9/9front/sys/src/cmd/dtracy/agg.c

This file implements user-space aggregation result collection for dtracy. Kernel aggregation records are parsed into per-aggregation AVL trees keyed by the aggregation key bytes.

Key responsibilities:
- Defines `ANode`, an AVL node containing key bytes plus aggregate state (`val`, `cnt`, `sq`).
- Initializes one AVL tree per aggregation in `agginit`.
- Parses aggregation buffers in `aggparsebuf`, validates IDs, key sizes, and record bounds, then creates or updates tree nodes.
- Handles aggregation types: count, sum, min/max storage, average, and standard deviation.
- Prints aggregation keys and values in `aggdump`.

Important implementation notes:
- `aggparsebuf` validates that the packed record ID type and key size match the corresponding `Agg`.
- Standard deviation uses Plan 9 multiprecision integers (`mp`) in `variance` to avoid overflow when combining squared sums.
- `aggnote` marks interruption so the aggregation reader can stop and dump accumulated results.
- `aggkeyprint` currently assumes an 8-byte integer key and formats `*(u64int*)a->key`.
