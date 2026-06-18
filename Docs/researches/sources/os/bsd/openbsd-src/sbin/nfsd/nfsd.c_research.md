# File Research: sources/os/bsd/openbsd-src/sbin/nfsd/nfsd.c

Purpose: Userland NFS server daemon wrapper. It starts kernel NFS server contexts, creates/registers UDP/TCP NFS sockets with portmap, and passes sockets into the kernel through `nfssvc()`.

Startup:
- Parses `-n num_servers`, `-r`, `-t`, and `-u`, plus legacy trailing daemon count.
- Defaults to UDP if neither TCP nor UDP is requested.
- Daemonizes outside DEBUG builds and ignores terminal signals.
- Unveils `/` with no permissions, then locks unveil.

Reregister mode:
- With `-r`, only registers requested NFS v2/v3 UDP/TCP mappings with portmap on `NFS_PORT`, then exits.

Server process model:
- Forks `nfsdcnt` worker children, each calling `nfssvc(NFSSVC_NFSD, &nsd)` and acting as a kernel NFS server context.
- Parent optionally creates a UDP socket bound to `NFS_PORT`, registers it, and passes it to the kernel with `NFSSVC_ADDSOCK`.
- For TCP, parent creates/listens on `NFS_PORT`, registers with portmap, accepts connections forever, enables keepalive, and passes accepted sockets to `NFSSVC_ADDSOCK`.

Signals:
- `SIGCHLD` handler reaps children with `wait3(WNOHANG)`.
- `SIGSYS` handler logs that NFS syscall support is missing.

Error handling:
- Uses syslog; initial openlog uses `LOG_PERROR` until after daemon setup, then switches to daemon log only.
