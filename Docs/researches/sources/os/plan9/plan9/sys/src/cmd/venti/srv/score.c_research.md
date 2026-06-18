# File Research: sources/os/plan9/plan9/sys/src/cmd/venti/srv/score.c

Purpose: Score helpers for Venti SHA1 content addresses.

Key behavior:
- Defines global `zeroscore`.
- `scoremem` computes SHA1 over a memory buffer.
- `strscore` parses a fixed-width hex score string into bytes.

Dependencies:
- Uses `libsec` SHA1 and Venti score constants.

Notable details:
- `needzeroscore` exists solely to force linking of `score.o` on OS X.
