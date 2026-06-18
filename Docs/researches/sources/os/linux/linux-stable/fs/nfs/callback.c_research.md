# File Research: sources/os/linux/linux-stable/fs/nfs/callback.c

## Purpose

`callback.c` owns the NFSv4 callback service lifecycle. It creates the SUNRPC service, starts/stops callback worker threads, binds callback transports per network namespace, manages v4.0 callback sockets and v4.1+ backchannel service attachment, and authenticates callback RPC credentials at the service layer.

## Main Responsibilities

- Maintain per-minor-version callback service state in `nfs_callback_info[]`.
- Create TCP callback listeners for NFSv4.0 over IPv4 and IPv6.
- Attach the callback `svc_serv` to the RPC transport for NFSv4.1+ backchannels.
- Start a bounded number of callback service threads.
- Track per-net and global callback service users.
- Tear down transports and service threads when the last user exits.
- Validate callback authentication flavor and GSS principal constraints.
- Define the NFSv4 callback SUNRPC program and version table.

## Key Functions

- `nfs_callback_up()` is the main start path. It creates or reuses a service, brings up per-net callback resources, starts service threads, and increments usage.
- `nfs_callback_down()` decrements per-net/global usage, destroys transports, stops threads, and nullifies backchannel service references when unused.
- `nfs_callback_create_svc()` creates the SUNRPC service with `nfs4_callback_svc()` as the worker thread function.
- `nfs_callback_start_svc()` records the backchannel service on minor versions greater than zero and calls `svc_set_num_threads()`.
- `nfs_callback_up_net()` binds the service to a network namespace and selects either v4.0 socket listeners or v4.1 backchannel enablement.
- `check_gss_callback_principal()` validates v4.0 RPCSEC_GSS callbacks against the negotiated acceptor or `nfs@hostname`.
- `nfs_callback_authenticate()` rejects non-NULL auth for non-`CB_NULL` NULL-auth requests and rejects GSS on backchannel callbacks.

## Control Flow and State

All start/stop operations are serialized by `nfs_callback_mutex`. Each minor version has its own `nfs_callback_data` with user count and `svc_serv`. Each network namespace tracks callback users by minor version in `nn->cb_users[]` and stores assigned v4.0 TCP ports. The callback kernel thread repeatedly calls `svc_recv()` until the service thread is asked to stop.

## Integration Points

- Uses `callback_xdr.c` exported `nfs4_callback_version1` and `nfs4_callback_version4`.
- Called by NFSv4 client setup and teardown paths when callback support is needed.
- Uses SUNRPC service, socket, auth, and backchannel APIs.
- Uses `struct nfs_net` fields for per-net callback ports and usage.

## Risks and Edge Cases

- v4.0 requires externally reachable callback listener sockets; failures in IPv4 or non-`EAFNOSUPPORT` IPv6 creation abort callback setup.
- v4.1+ requires transport backchannel support via `xprt->ops->bc_setup`.
- GSS callback validation is intentionally limited for v4.1 backchannel, which is rejected here.
- Service destruction is tied to exact user counting; incorrect up/down pairing would leak or prematurely destroy the callback service.

## Testing Focus

Exercise v4.0 IPv4/IPv6 listener setup, v4.1 backchannel setup, module/thread count boundaries, failed service creation rollback, GSS principal validation, invalid auth flavor rejection, and multi-net namespace up/down reference behavior.
