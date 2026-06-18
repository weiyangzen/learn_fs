# File Research: sources/os/plan9/9front/sys/src/cmd/venti/srv/fixarenas.c

Large recovery utility for damaged arena partitions or standalone arenas.

Key behavior:
- Can run read-only or with `-f` to write repairs. Supports arena size/block size hints, base name override, unsealing, verbose output, and dumping recovered arenas.
- `readdisk` handles failed reads by retrying progressively smaller chunks down to 512-byte sectors, filling unreadable regions with marker bytes and coalescing bad-sector reports.
- Uses a 4 MiB mutable paging buffer; edits are written back only when `fix` is enabled.
- `Shabuf` maintains SHA-1 state, optional debug dump output, and rollback checkpoints every 4 MiB for resealing after edits.
- `guessgeometry` scans surviving arena heads/tails to infer arena size, block size, and arena base when the partition header is corrupt.
- `checkarenas` validates/rewrites the arena partition superblock and checks selected arena ranges.
- `isclump` validates candidate clumps by magic/type/sizes, decompression if compressed, and SHA-1 score.
- Maintains recovered clump-info entries in `cibuf`, with a score tree for duplicate detection.
- `guessarena` reconstructs arena basics, scans clump data, zeros corrupt regions when fixing, creates corrupt clump-info entries as needed, reconstructs/writes clump-info directory, recomputes stats, and optionally reseals.
- `checkarena` compares packed header/tail/seal against reconstructed values and writes corrected blocks when fixing.
- `checkmap` rebuilds the arena partition map from recovered arena headers and rewrites it if different.

Interactions:
- Reuses pack/unpack routines from `conv.c`, compression from `whack.h`, and arena map output logic.
- More tolerant than normal server code because it must recover past local corruption.

Notable issues:
- `vlongcmp` appears wrong: after `if(a < b) return -1;`, it checks `if(b > a) return 1;`, which repeats the same condition rather than checking `a > b`.
- Contains unconditional debug prints such as `old arena: sealed=...` and `eoffset=...`.
- Comments note unfinished geometry/table improvements.
