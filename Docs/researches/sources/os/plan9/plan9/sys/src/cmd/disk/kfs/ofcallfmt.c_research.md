# File Research: sources/os/plan9/plan9/sys/src/cmd/disk/kfs/ofcallfmt.c

This file implements `%O` formatting for old 9P1 `Oldfcall` messages.

Key behavior:
- `ofcallfmt` switches on the 9P1 message type and formats a human-readable summary with tag, fid, qid, names, modes, counts, errors, or stat data.
- `fdirconv` formats decoded old stat records as dentry-like metadata.
- `dumpsome` prints up to 24 bytes of read/write payload as printable text or hex.

Dependencies:
- Uses `Oldfcall` definitions from `9p1.h`.
- Uses `convM2D9p1` to decode stat buffers.
- Registered by `formatinit` in `sub.c`.

Role:
- Debug/trace support for `chat` mode in 9P1 serving and console dispatch.
