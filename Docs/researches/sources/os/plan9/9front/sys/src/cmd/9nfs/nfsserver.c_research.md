# File Research: sources/os/plan9/9front/sys/src/cmd/9nfs/nfsserver.c

This file is the main NFS v2 server implementation over the shared RPC server framework.

Key content:
- Defines the NFS procedure table for program `100003`, version 2.
- Defines a combined `progmap` registering both mount program `100005` and NFS program `100003`.
- `main` starts the RPC server on port 2049.
- `nfsinit` installs periodic alarm logic for fid expiration and UID-map reloads.
- `doalarm` updates `nfstime`, runs mount timers, and reloads config periodically.

Implemented NFS handlers:
- `nfsgetattr`, `nfssetattr`, `nfslookup`, `nfsread`, `nfswrite`, `nfscreate`, `nfsremove`, `nfsrename`, `nfsmkdir`, `nfsrmdir`, `nfsreaddir`, and `nfsstatfs`.
- Stub/error handlers for `nfsreadlink`, `nfslink`, and `nfssymlink`.
- `nfsnull`, `nfsroot`, and `nfswritecache` provide simple protocol responses.

Important interactions:
- Uses `rpc2xfid` and the `Xfile`/`Xfid` bridge from `nfs.c`.
- Translates errors into NFS status codes using `error`.
- Reads/writes through 9P `Tread`, `Twrite`, `Twalk`, `Topen`, `Tcreate`, `Tremove`, and `Twstat` via helper routines.
- Directory reads convert Plan 9 packed `Dir` records into NFS directory entries.

Research notes:
- Write and read counts are bounded by message size/8192-byte buffers.
- Rename only supports same-directory renames because source and target handles must match.
- `statfs` returns synthetic large free-space values rather than querying backing storage.
