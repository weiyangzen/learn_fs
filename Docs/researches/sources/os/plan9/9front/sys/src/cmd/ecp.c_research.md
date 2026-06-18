# File Research: sources/os/plan9/9front/sys/src/cmd/ecp.c

This file implements `ecp`, a robust sector-oriented copy tool designed for failing media. It copies in large blocks when possible, falls back to single-sector transfers on errors, can verify after copy, and can copy in reverse.

Key responsibilities:
- Tracks source and destination state in `File`, including start sector, seekability, hard errors, consecutive errors, and fast/slow transfer mode.
- Reads/writes blocks with `bio`, handling short reads, optional reblocking, and zero-filling.
- Retries failed large transfers sector by sector in `bigxfer`.
- Reports bad sector ranges compactly with `io_expl` and `ckendrange`.
- Verifies copied data in a separate pass through `verify`/`vrfysects`.
- Supports confirmation, progress, reverse copy, start offsets, sector size, block size, max consecutive errors, and byte swizzling.

Important implementation notes:
- `copyfile` creates the destination if missing, then opens source and destination with seekability checks.
- Verification is intentionally separate from copying to avoid controller-cache false confidence.
- `swizzlebits` rotates and inverts bytes for the `-Z` mode.
