<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/nfsd/nfsd.c -->
# sources/user-network-fs/nfs-utils/utils/nfsd/nfsd.c

## Purpose

`nfsd.c` is the command-line front end for starting, stopping, and configuring kernel NFS server threads. The kernel performs NFS serving; this program configures versions, protocols, sockets, RDMA, grace/lease times, scope, and thread count.

## Important APIs, types, and functions

`main` owns all behavior. `read_nfsd_conf` initializes config and debug settings. The option parser handles host, scope, version enable/disable, TCP/UDP, port, RDMA, grace time, lease time, syslog, and debug. It calls `nfssvc_get_minormask`, `nfssvc_mount_nfsdfs`, `nfssvc_inuse`, `nfssvc_setvers`, `nfssvc_set_time`, `nfssvc_set_sockets`, `nfssvc_set_rdmaport`, and `nfssvc_threads`.

## Control flow

Startup reads defaults from `nfs.conf`, folds in command-line options, validates requested version/protocol combinations, changes into `NFS_STATEDIR`, ensures nfsdfs is mounted, and checks whether nfsd sockets are already configured. For a fresh start it writes version and timeout settings first, optionally unshares UTS namespace and sets hostname scope, opens requested TCP/UDP sockets per host and hands them to the kernel, optionally requests RDMA, then closes inherited fds and writes the desired thread count. If thread count is zero, it skips socket setup and only changes thread count.

## State and persistence behavior

Persistent server state lives in the kernel and procfs/nfsdfs files, not in this process. The program may alter the UTS namespace hostname for NFSv4 scope when `--scope` is used. It switches logging to syslog before closing standard descriptors.

## Dependencies and integration points

It depends on config parsing, support NFS control bit macros, `nfssvc.c`, `xlog`, `basename`, sockets, and Linux `unshare(CLONE_NEWUTS)`. It integrates directly with `/proc/fs/nfsd` through `nfssvc.c`.

## Risks and edge cases

Version/minor-version bit logic is subtle, especially force-setting v4.0 on newer kernels. NFSv4 requires TCP and is rejected without it. Existing nfsd sockets prevent reconfiguration beyond thread count. Host list reallocation has precedence-sensitive sizing code. Closing all fds before spawning threads protects the kernel but makes late stderr diagnostics unavailable.

## Test signals

Tests should cover config and CLI precedence, enabling/disabling v3/v4 minors, all-versions-disabled rejection, v4-without-TCP rejection, `nrservs=0`, existing nfsd in-use path, invalid ports and times, host lists, RDMA option forms, scope setup failures, and socket failure propagation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/nfsd/nfsd.c -->
