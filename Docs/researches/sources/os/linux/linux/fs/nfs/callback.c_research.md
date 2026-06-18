# File Research: sources/os/linux/linux/fs/nfs/callback.c

## Purpose
Creates, starts, authenticates, and tears down the NFSv4 callback RPC service. This is the server-side service inside the NFS client that receives callbacks from NFSv4 servers.

## Main Responsibilities
- Maintain callback service instances by NFSv4 minor version.
- Create TCP callback listeners for NFSv4.0.
- Enable RPC backchannel service for NFSv4.1+ sessions.
- Start and stop callback service threads.
- Track per-network-namespace callback users.
- Authenticate callback RPC requests.
- Define the NFSv4 callback RPC program.

## Key Functions
- `nfs_callback_up()` creates or reuses the callback service, binds per-net transport/backchannel state, starts service threads, and increments user counts.
- `nfs_callback_down()` decrements users, destroys per-net transports, stops service threads, and clears backchannel service pointers when no users remain.
- `nfs4_callback_svc()` is the callback service thread loop using `svc_recv()`.
- `nfs4_callback_up_net()` creates IPv4 and optionally IPv6 TCP listener sockets for v4.0 callbacks.
- `nfs_callback_up_net()` binds the service to a net namespace and either starts v4.0 listeners or enables v4.1+ backchannel support.
- `check_gss_callback_principal()` validates RPCSEC_GSS callback principals for NFSv4.0.
- `nfs_callback_authenticate()` enforces basic auth flavor rules before XDR-level client lookup.

## Control Flow
`nfs_callback_up()` is serialized by `nfs_callback_mutex`. It creates a `svc_serv` if needed, initializes per-net callback state, then ensures the service has at least `NFS4_MIN_NR_CALLBACK_THREADS` threads. Error paths undo per-net setup and destroy the service if there are no users.

## Data and Ownership
- `nfs_callback_info[minorversion]` stores service pointer and global user count.
- Per-net `nn->cb_users[minorversion]` tracks network namespace use.
- For v4.1+, `xprt->bc_serv` stores the service for backchannel initialization.

## Authentication Behavior
- `RPC_AUTH_NULL` is accepted only for `CB_NULL`.
- `RPC_AUTH_GSS` is denied on backchannel callbacks.
- Detailed NFSv4.0 client/principal validation is deferred to compound processing after the callback identifier resolves to an `nfs_client`.

## Notable Details
- IPv6 listener failure is ignored only for `-EAFNOSUPPORT`.
- Callback thread count is module-configurable but clamped to at least one.
- v4.1 callback concurrency is effectively constrained by backchannel slot constants in `callback.h`.

## Risks and Edge Cases
- `nfs_callback_down()` assumes matching up/down calls; underflow of user counts would be serious.
- GSS principal fallback compares `nfs@hostname` to `cl_hostname`, which can fail for non-canonical mount names.
- v4.1+ GSS callback support is explicitly absent.

## Integration Points
Uses callback procedure versions from `callback_xdr.c`, client records from `client.c`, and NFS net namespace state from `netns.h`.
