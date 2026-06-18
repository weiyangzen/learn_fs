# File Research: sources/os/plan9/plan9/sys/src/cmd/venti/srv/reseal.c

Purpose: Verifies and rewrites sealed arena trailer/checksum data.

Key behavior:
- Reads an arena partition table, optionally filters named arenas, and reseals matching sealed arenas.
- `verify` hashes all arena bytes with the seal slot treated as zero, compares with the stored score unless forced, repacks the arena trailer, computes the new score, and writes it into the trailer.
- `resealarena` validates the arena head/tail, skips unsealed arenas, writes the new tail, and verifies again.
- Supports block-size override, force mode, and optional sleep delay.

Dependencies:
- Uses low-level `pread`/`pwrite`, arena head/trailer packing, SHA1, partition metadata parsing, and `unittoull`.

Notable details:
- `force` allows resealing even when the old checksum does not match, with a warning.
