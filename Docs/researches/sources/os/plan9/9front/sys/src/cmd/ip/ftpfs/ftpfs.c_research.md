# File Research: sources/os/plan9/9front/sys/src/cmd/ip/ftpfs/ftpfs.c

9P filesystem front end for mounting an FTP server. It logs in, builds a mirror tree of `Node` objects, forks a 9P server side, and mounts it at `/n/ftp` or a requested mountpoint.

Implements core 9P messages: version, attach, walk, open, create, read, write, clunk, remove, stat, and error stubs for auth/wstat. Directories are populated from remote listings; files are fetched into the local cache on open/read and uploaded with `createfile` when dirty on clunk/uncache.

Supports cache invalidation through `.flush.ftpfs`, optional persistent cache, keepalive process, remote OS selection, TLS mode, anonymous password mode, mount root selection, and filename extension decoration.
