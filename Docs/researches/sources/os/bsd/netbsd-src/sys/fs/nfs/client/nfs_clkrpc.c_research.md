# File Research: sources/os/bsd/netbsd-src/sys/fs/nfs/client/nfs_clkrpc.c

This file implements kernel RPC service support for NFSv4 client callbacks. It lets a user-supplied callback socket be taken over by the kernel and serviced by the `nfscbd` RPC pool.

Key entry points:
- `nfscb_program()` is the registered RPC dispatch function for callback requests.
- `nfs_cbproc()` invokes `nfscl_docb()` and maps its result to reply/drop behavior.
- `nfscbd_addsock()` reserves socket buffers, creates an RPC transport, steals the socket from the file descriptor, and registers `NFS_CALLBCKPROG`.
- `nfscbd_nfsd()` runs the callback service pool, optionally registering a Kerberos service principal for RPCSEC_GSS callbacks.
- `nfsrvd_cbinit()` initializes the callback service pool and synchronizes termination.

Important behavior:
- Only `NFSPROC_NULL` and `NFSV4PROC_CBCOMPOUND` are accepted.
- Non-null callbacks realign the request mbuf, capture caller address data, obtain credentials, and dispatch through `nfscl_docb()`.
- `NFSERR_DONTREPLY` causes the callback request to be dropped rather than answered.
- Only the first `nfscbd` caller runs the service pool; extra callers return after observing that a callback daemon is already active.
- `nfscbd_pool` is created lazily by `nfsrvd_cbinit()`.

Dependencies:
- Uses kernel RPC server APIs (`svc_dg_create()`, `svc_vc_create()`, `svc_reg()`, `svc_run()`, `svc_sendreply_mbuf()`).
- Shares `nfscbd_pool`, `nfs_numnfscbd`, and `NFSDLOCKMUTEX` state with the wider NFS service framework.
- Calls NFSv4 callback executor `nfscl_docb()`.

Research notes:
- This is callback server plumbing for the client, not normal outbound client RPC.
- Socket ownership transfer in `nfscbd_addsock()` is significant: the file is neutered with `badfileops` and `f_data = NULL` once the transport is created.
