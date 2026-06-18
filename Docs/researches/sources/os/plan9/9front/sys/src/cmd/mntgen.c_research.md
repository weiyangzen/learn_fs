# File Research: sources/os/plan9/9front/sys/src/cmd/mntgen.c

Implements `mntgen`, a small dynamic 9P server that creates ephemeral directory entries on walk.

Key behavior:
- Serves read-only directories under a mount point or service name.
- Root directory dynamically creates a child directory when a new name is walked.
- Child directories are empty; walking `..` returns to root.
- Tracks entries in `Tab` records keyed by a 48-bit MD5-derived qid path and reference counts.
- Removes entries when their final fid is clunked.
- Supports `-s srvname` and `-D` chatty 9P mode.

Important dependencies: Plan 9 `thread`, `9p`, `fcall`, `libsec` MD5, `postmountsrv`.

Notable risks:
- Hash collisions are detected but make the walked name fail.
- Entries exist only while referenced; clients relying on stable listing need open fids.
