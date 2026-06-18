# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/nfsmount.c

Small SunRPC/NFSv3 mount protocol client. It connects to a host, optionally asks portmap for the NFS mount daemon port, then runs one mount-protocol command.

Commands:
- `null`
- `mnt path`
- `dump`
- `umnt path`
- `umntall`
- `export` default

Core behavior:
- Uses `libsunrpc` and generated `nfs3.h` mount structures.
- `getport()` performs a portmapper `GETPORT`.
- `mountCall()` fills SunRPC program/version/procedure metadata and attaches AUTH_SYS credentials for calls.
- `tmnt()` prints the returned NFS file handle and accepted auth flavors.
- `tdump()` prints current mount entries.
- `texport()` unpacks and prints exported paths and groups.

Dependencies and integration:
- Includes `<thread.h>`, `<sunrpc.h>`, and `<nfs3.h>`.
- Uses Plan 9 thread entry `threadmain()`.
- Shares protocol idioms with `portmap.c`.

Notable risks:
- Static fake AUTH_SYS credential `unixauth` is hard-coded as user/group 1001 and host `gnot`.
- `tab` declares `umntall` as requiring one argument even though usage says none and `tumntall()` ignores arguments; this looks like a command table bug.
- Port rewriting assumes network address contains `!`.
