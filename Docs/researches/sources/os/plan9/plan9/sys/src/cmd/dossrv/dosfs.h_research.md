# File Research: sources/os/plan9/plan9/sys/src/cmd/dossrv/dosfs.h

Tiny protocol constants header for `dossrv`.

Key contents:
- `Maxfdata = 8192`.
- `Maxiosize = IOHDRSZ + Maxfdata`.

Filesystem relevance:
- Caps 9P payload sizing used by request and response buffers.
