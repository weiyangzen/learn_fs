# File Research: sources/os/plan9/plan9/sys/src/cmd/nfs.c

Implements a Plan 9 9P server front-end for NFSv3. It dials mount and NFS RPC services, optionally discovers ports through portmap, mounts an exported NFS path, and exposes the result through `threadpostmountsrv`.

Core logic is split between SunRPC/NFS wrappers and 9P request handlers. RPC helpers wrap `MOUNT`, `GETATTR`, `ACCESS`, `LOOKUP`, `READ`, `WRITE`, `READDIR`, `READDIRPLUS`, `CREATE`, `MKDIR`, `REMOVE`, `RMDIR`, `RENAME`, `SETATTR`, and `COMMIT`, translating NFS status to Plan 9 error strings. `FidAux` stores the NFS handle, parent handle, name, readdir cookie, and auth data for each fid.

The file maps Unix passwd/group data to Plan 9 names and SunAuthUnix credentials when `-u passwd group` is supplied. Unknown users fall back to nobody-style uid/gid `-1` credentials.

The 9P layer translates NFS attributes into Plan 9 `Qid`/`Dir`, performs permission checks through NFS `ACCESS`, serves directory reads by converting NFS directory entries to 9P stat records, and handles walk/clone/remove/wstat semantics. Rename plus setattr is explicitly non-atomic.

Operationally, `threadmain` handles `-D`, `-R`, `-v`, `-p`, `-s`, and `-u`, discovers mount/NFS ports if only one address is supplied, starts a dial helper process, then posts the service. `Tflush` forwards tags to both RPC clients’ flush channels.
