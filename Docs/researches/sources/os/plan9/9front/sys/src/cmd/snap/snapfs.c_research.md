# File Research: sources/os/plan9/9front/sys/src/cmd/snap/snapfs.c

Purpose: Mounts a snapshot file as a read-only `/proc`-like 9P filesystem.

Behavior:
- Reads snapshot with `readsnap`.
- Builds a lib9p tree with one directory per process.
- Creates `ctl`, `mem`, optional `text`, and captured proc-file entries.
- `fsread` dispatches to `memread` for `mem`/`text` virtual files or `dataread` for captured metadata.
- Default mount point is `/proc`; `-a` mounts after existing contents; `-m` changes mount point.

Integration: Uses lib9p file tree APIs and `findpage` from `read.c`.

Risks:
- `memread` reads only within one 1024-byte snapshot page per request.
- `ctl` is created but has no special behavior.
- Mounting over `/proc` changes process namespace semantics for clients.
