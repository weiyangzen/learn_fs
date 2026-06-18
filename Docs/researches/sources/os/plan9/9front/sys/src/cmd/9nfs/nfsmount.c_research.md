# File Research: sources/os/plan9/9front/sys/src/cmd/9nfs/nfsmount.c

This file implements the NFS mount protocol service and initializes backing 9P sessions.

Key routines:
- `mntinit` parses mount/server options, initializes one or more 9P services, reads UID maps, sets `starttime`, and configures stale-fid timeout.
- `srvinit` opens/dials/uses a 9P connection, negotiates `Tversion`, authenticates, attaches as `none`, creates root `Xfile`/`Xfid` state, and links the session into the service list.
- `mnttimer` invokes per-session fid expiration.
- Mount RPC handlers: `mntnull`, `mntmnt`, `mntdump`, `mntumnt`, `mntumntall`, and `mntexport`.
- `xfroot` resolves a mount root name or service alias to a session root.

Important interactions:
- `nfsserver.c` registers this as program `100005`, version 1.
- Uses `authhostowner`, `xmesg`, `newfid`, `xfile`, `xfid`, `xp2fhandle`, and UID-map functions.
- Maintains global `head`/`tail` session list.

Research notes:
- `noauth` is forced on with `noauth=1; /* ZZZ */`, disabling some auth behavior regardless of option parsing.
- Default service is `tcp!fs` if none is configured.
- Export replies expose `/` and optionally the AUTH_UNIX machine name.
