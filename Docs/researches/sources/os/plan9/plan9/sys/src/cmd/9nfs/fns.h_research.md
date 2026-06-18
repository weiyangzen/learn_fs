# File Research: sources/os/plan9/plan9/sys/src/cmd/9nfs/fns.h

Purpose: shared function prototypes for 9nfs.

Key behavior: declares RPC, NFS, auth, session, fid, xfile, name mapping, string table, server, logging, and utility functions.

Integration notes: complements `dat.h`; signatures show the main subsystem boundaries even for files not in this group, such as `server.c`, `xfile.c`, and uid-map readers.
