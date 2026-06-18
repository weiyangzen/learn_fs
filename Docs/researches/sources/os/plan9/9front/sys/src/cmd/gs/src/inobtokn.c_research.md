# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/inobtokn.c

Level 1 stub implementation for binary token scanning.

Key behavior:
- Defines `scan_binary_token`.
- Always returns `e_unregistered`.

Notable dependencies:
- `ghost.h`, `ierrors.h`, `stream.h`, `iscan.h`, and `iscanbin.h`.

Research notes:
- This is the fallback module used when binary-token support is not built.
- `int.mak` packages it into `nobtoken.dev`; full binary token support replaces it with `btoken.dev`.
