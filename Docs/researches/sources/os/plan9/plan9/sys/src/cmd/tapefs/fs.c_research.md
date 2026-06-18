# File Research: sources/os/plan9/plan9/sys/src/cmd/tapefs/fs.c

This file is the common tapefs 9P server that serves an archive/image as a mounted read-only filesystem.

Key behavior:
- Builds a root `Ram` tree, calls the selected backend `populate`, forks an I/O server, and mounts it at `/n/tapefs` or `-m mountpoint`.
- Implements core 9P requests: version, attach, walk, open, read, write, clunk, stat, flush, and errors for create/remove/wstat/auth.
- Serves directories by converting `Ram` entries to Plan 9 stat records.
- Serves files by delegating content reads to backend `doread`.
- Lazily populates unreplete directories through backend `popdir`.

Important details:
- The filesystem is effectively read-only: `perm(Pwrite)` returns false and create/remove/wstat return permission errors.
- Fids track open state, user, and current `Ram` node.
- Message size is negotiated by `Tversion` and capped by `Maxbuf+IOHDRSZ`.
- `io()` runs the 9P request loop over a pipe used as the mount fd.

Filesystem relevance:
- Central: generic 9P façade for tape/archive/filesystem-image backends.
