# File Research: sources/os/plan9/plan9/sys/src/cmd/cifs/main.c

Main 9P server for mounting remote CIFS shares. It maintains per-fid `Aux` state: current path/share, open file handle, search handle, directory cache window, and linked-list tracking for diagnostics/cleanup.

Implements 9P attach, clone, walk, stat, open, create, read, write, remove, wstat, destroyfid, and server end. Directory reads use Trans2 find-first/find-next with a short cache. Walk/stat convert SMB metadata to Plan 9 `Dir` via `FInfo`; Qids are SHA1-derived from paths plus subtype bits for root/info/share nodes. Open/create choose NT SMBs when available, otherwise legacy SMBs.

`main` parses options, discovers/dials the server, negotiates, authenticates, connects `IPC$`, enumerates or connects requested shares, starts a keepalive process, and posts/mounts the 9P service. Wstat handles rename, length, times, readonly bit, and flushes open files to work around old Windows caching behavior.
