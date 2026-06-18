# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/inobtokn.c

Level 1 dummy implementation for binary-token scanning.

Key behavior:
- Includes interpreter/scanner headers: `ghost.h`, `ierrors.h`, `stream.h`, `iscan.h`, and `iscanbin.h`.
- Defines `scan_binary_token`.
- Always returns `e_unregistered`.

Research notes:
- This file backs the `nobtoken` module in `int.mak`; full binary-token support is supplied by `iscanbin.c` when the `btoken` feature replaces it.
