# File Research: sources/os/plan9/plan9/sys/src/cmd/disk/kfs/dat.h

This header defines KFS runtime structures layered above the on-disk structures in `portdat.h`.

Key contents:
- Includes `portdat.h`.
- Defines `Chan`, the per-connection state: fd, read/write locks, fid list, flush/ref lock, negotiated msize, auth state, and old 9P1 challenge/replay fields.
- Defines `Cons`, the console state: flags, temporary create uid/gid, argument cursor, console channels, and load/stat filters.
- Defines `Conf`, runtime sizing parameters.
- Defines `Command`, command-table entries.
- Defines `Devcall`, the device method table.
- Defines device and filesystem constants, qid compatibility constants, old create mode flags, fid constants, time macros, and `CHAT`.
- Declares global state from `dat.c` and other modules.

Role:
- Main shared runtime ABI for the KFS server.
- Bridges protocol, console, device, auth, and block-cache code.

Notable detail:
- `CHAT(cp)` ignores its argument and expands to global `chat`, which is why some code can call `CHAT` with non-existent local names after macro expansion.
