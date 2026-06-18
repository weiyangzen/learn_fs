# File Research: sources/os/plan9/plan9/sys/src/cmd/9nfs/dat.h

Purpose: shared protocol/session/xfile data model for 9nfs.

Key behavior: defines RPC call/reply/auth structs, NFS file handles, uid/gid mapping structs, cached xfile and per-user xfid state, fid LRU records, sessions with 9P message buffers and fid pool, challenge state, and global configuration declarations.

Integration notes: central contract between RPC server, mount service, NFS service, auth, name mapping, 9P session management, and xfile cache.
