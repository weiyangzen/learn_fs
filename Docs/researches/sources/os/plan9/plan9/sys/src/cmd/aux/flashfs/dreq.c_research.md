# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/flashfs/dreq.c

This file is an alternate or dummy 9P request layer for flashfs.

Key behavior:
- Defines fid state holding an `Entry` and optional directory reader.
- Implements attach, open, create, read, write, remove, stat, wstat, and walk handlers.
- Directory reads use `edirread`.
- Metadata operations delegate to entry routines such as `ecreate`, `etrunc`, `eremove`, `echmod`, and `estat`.
- Mounts with `postmountsrv` under service name `brzr`.

Important details:
- Regular file reads return zero bytes and regular file writes only acknowledge bytes, so payload I/O is not implemented here.
- `flwalk` rejects all walks when `readonly` is set, which makes read-only traversal unusable in this version.
- The complete journaled request path appears in `request.c`.

Filesystem relevance:
- Direct but incomplete: skeletal flashfs 9P server layer.
