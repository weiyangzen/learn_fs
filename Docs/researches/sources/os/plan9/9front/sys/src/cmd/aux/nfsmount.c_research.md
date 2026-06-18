# File Research: sources/os/plan9/9front/sys/src/cmd/aux/nfsmount.c

`nfsmount` is an RPC client for the NFSv3 mount protocol. It can call mountd procedures `null`, `mnt path`, `dump`, `umnt path`, `umntall`, and `export`, with `export` as default.

It optionally contacts the portmapper first to resolve the mountd port, then reconnects to the NFS mount program. Calls are constructed with `SunCall` metadata and, for mount calls, a hard-coded AUTH_SYS credential for user/group 1001 and machine name `gnot`.

Options: `-R` enables chatty RPC tracing, `-m` disables portmapper lookup. It uses `libsunrpc` and generated `nfs3` mount structures, including unpacking export and mount-list payloads.

Notable issue: command table lists `umntall` with `narg` 1 even though the function ignores arguments and usage says none.
