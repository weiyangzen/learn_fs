# File Research: sources/os/plan9/9front/sys/src/cmd/ramfs.c

This file implements `ramfs`, a user-space in-memory 9P filesystem using lib9p.

Key responsibilities:
- Stores file contents sparsely in 64 KiB chunks under an indirect `Ram` array.
- Uses a custom Plan 9 `Pool` backed by `sbrk`, with relocation repair through `rammoved()`.
- `fsread()` reads file data, returning zeros for holes.
- `fswrite()` expands indirect/data chunks as needed, honors append mode, zero-fills gaps, and enforces `MAXFSIZE`.
- `truncfile()` shrinks or frees backing chunks.
- `fswstat()` implements rename, chmod-like mode changes, group changes, length changes, and timestamp updates with Plan 9-style permission checks.
- `fscreate()`, `fsopen()`, `fsdestroyfid()`, and `fsdestroyfile()` implement create/open/remove-on-close/free behavior.
- `fsstart()` can mark the process memory private and unswappable when `-p` is used.
- `main()` configures mount/server modes and posts the service through stdio, `/srv`, or a mountpoint.

Options:
- `-i` serves on stdin/stdout.
- `-s`/`-S` post service names.
- `-m` chooses mountpoint.
- `-p` protects memory.
- `-u` removes the default pool size cap.
- `-a`, `-b`, `-c` adjust mount flags.

Implementation notes:
- Exclusive files use a 300-second lock check based on refs and atime.
- ORCLOSE removes files on fid destruction.
