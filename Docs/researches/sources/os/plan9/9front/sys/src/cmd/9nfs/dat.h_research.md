# File Research: sources/os/plan9/9front/sys/src/cmd/9nfs/dat.h

This header defines the shared data model for `9nfs`.

Key structures:
- RPC-related: `Auth`, `Authunix`, `Accept`, `Reject`, `Rpccall`, and `Rpccache`.
- NFS/data conversion: `Fhandle`, `Sattr`, `String`.
- UID mapping: `Unixid`, `Unixmap`, `Unixidmap`, and `Unixscmap`.
- Namespace/session: `Xfile`, `Xfid`, `Fid`, `Session`, and `Chalstuff`.
- Program dispatch: `Progmap` and `Procmap`.

Important fields:
- `Rpccall` includes UDP-header-derived host/port fields and RPC call/reply unions.
- `Xfile` caches a 9P qid tree and maps it to NFS file handles.
- `Xfid` binds a user to an `Xfile` with cached user/root and open fids.
- `Session` holds the underlying 9P connection, message buffer, fid pool, root, service name, and auth flags.

Important interactions:
- Used by NFS server, mount server, PC-NFS server, RPC parser/serializer, auth, and UID-map code.
- Defines constants such as `FHSIZE`, `Maxfdata`, and `Maxstatdata`.

Research notes:
- The design is a stateful bridge from stateless NFS file handles to cached 9P sessions/fids.
