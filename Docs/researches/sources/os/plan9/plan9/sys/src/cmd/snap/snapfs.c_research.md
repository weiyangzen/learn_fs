# File Research: sources/os/plan9/plan9/sys/src/cmd/snap/snapfs.c

9P filesystem server exposing a snapshot as a `/proc`-like tree.

Key behavior:
- Reads a snapshot file with `readsnap()`.
- Builds an in-memory 9P tree with one directory per pid.
- Creates files such as `ctl`, `text`, `mem`, and captured pseudo-files.
- Implements reads from `Data` blobs or memory/text pages via `findpage()`.
- Mounts by default before `/proc`, or after with `-a`, or at a custom mount point with `-m`.

Important details:
- `ctl` is created but has no custom write/control implementation here.
- `mem` and `text` reads are page-limited to one 1024-byte page segment.
- `-D` enables chatty 9P diagnostics and `-d` enables snapshot debug.

Filesystem relevance:
- Direct: serves snapshot data as a synthetic Plan 9 9P filesystem resembling `/proc`.
