# File Research: sources/os/bsd/freebsd-src/sys/fs/nfsclient/nfs_clkrpc.c

`nfs_clkrpc.c` implements kernel RPC server-side handling for NFS client callbacks (`nfscbd`), used primarily by NFSv4 callback operations from server to client.

Key functions and behavior:
- `nfscb_program()` is the RPC dispatch entry for callback requests. It accepts only null and callback compound procedures, constructs an `nfsrv_descript`, realigns incoming mbufs, captures caller addresses and credentials, enables external-page reply handling for KTLS when available, invokes callback processing, frees request resources, and sends mbuf replies or RPC errors.
- `nfs_cbproc()` marks stream sockets when appropriate, calls `nfscl_docb()` to execute the callback, and returns cache-style reply/drop actions.
- `nfscbd_addsock()` reserves socket buffer space, steals a userland socket from its file descriptor, creates datagram or connection RPC transport, registers callback program/version, and releases the transport reference.
- `nfscbd_nfsd()` services callback daemon requests from `nfssvc()`. It optionally installs a Kerberos service principal, starts the callback service pool with fixed thread counts, clears service names on exit, and coordinates singleton operation via `nfs_numnfscbd`.
- `nfsrvd_cbinit()` initializes or tears down the callback service pool, waiting for callback daemon registrations during termination and creating the `nfscbd` service pool when absent.

Important integration points:
- Uses kernel RPC service APIs (`svc_*`, `svcpool_*`) and RPCSEC_GSS/TLS support.
- Shares server-style descriptor/caching return conventions (`RC_DROPIT`, `RC_REPLY`) even though it handles client callbacks.
- Coordinates with global `nfscbd_pool`, `nfs_numnfscbd`, and NFS daemon lock macros.
- Callback authentication is intentionally permissive in the current path; comments discuss limitations and historical AUTH_SYS callback behavior.

Research notes:
- This file is control-plane callback plumbing, not normal client outbound RPC.
- Correct resource ownership is central: incoming request mbufs, credentials, sockets stolen from userland, service pool refs, and daemon lifecycle are all managed here.
