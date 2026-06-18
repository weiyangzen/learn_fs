# File Research: sources/os/bsd/netbsd-src/sys/fs/nfs/server/nfs_nfsdkrpc.c

Provides the kernel RPC front end for the NFS server. It registers NFS program versions on server sockets, converts incoming `svc_req` records into `nfsrv_descript`, authenticates credentials, enforces optional privileged-port policy for NFSv2/v3, coordinates duplicate request caching, dispatches actual NFS request execution, and sends mbuf replies.

`nfssvc_program()` is the main RPC dispatcher. It maps NFSv2 procedure numbers to generic server procedure numbers, validates supported NFS versions, realigns request mbufs, fetches RPC credentials and GSS flavor flags, takes the NFSv4 suspend shared reference, checks NFSv4 root export state, calls `nfs_proc()`, and sends or drops the reply based on duplicate-cache results.

`nfs_proc()` handles duplicate request cache lookup/update around `nfsrvd_dorpc()`. NFSv4.1 bypasses the classic DRC and uses session-slot reply caching. Earlier versions use `nfsrvd_getcache()`, `nfsrvd_updatecache()`, and `nfsrc_trimcache()`.

`nfsrvd_addsock()` steals a userspace socket into a kernel RPC transport and registers NFSv2/v3/v4 based on sysctl min/max versions. `nfsrvd_nfsd()` runs the service pool, optionally registers Kerberos service names, and tears down state on exit. `nfsrvd_init()` creates the `nfsd` service pool and installs FHA request assignment.

Important dependencies include krpc service transports, rpcsec_gss, FHA, duplicate cache code, NFSv4 root/suspend locks, `nfsrvd_dorpc()`, session caching, and shared `nfsd` module state.
