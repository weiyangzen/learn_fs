# File Research: sources/os/linux/linux/fs/lockd/svc.c

## Purpose
`svc.c` is the central lockd service module for Linux NFS/NLM locking. It owns creation and teardown of the single `lockd` RPC service, per-network-namespace lockd activation, listener socket setup, grace period timing, module/sysctl configuration, generic RPC dispatch, and netlink get/set operations for lockd server parameters.

## Main Responsibilities
- Maintains global service state through `nlmsvc_mutex`, `nlmsvc_users`, and `nlmsvc_serv`.
- Starts the lockd kernel thread with `svc_create()` and `svc_set_num_threads()`.
- Runs the lockd request loop in `lockd()`, retrying blocked NLM requests via `nlmsvc_retry_blocked()` before waiting in `svc_recv()`.
- Creates IPv4 and IPv6 UDP/TCP listeners using `svc_xprt_create()` and tears them down on per-net shutdown.
- Starts and ends NLM grace periods with the generic VFS lock grace APIs: `locks_start_grace()`, `locks_end_grace()`, and delayed work.
- Registers address notifiers so temporary transports tied to removed IP addresses can be aged out.
- Provides `lockd_up()` and `lockd_down()` as exported lifecycle entry points for NFS client/server users.
- Defines sysctls and module parameters for grace period, timeout, UDP/TCP ports, and NSM hostname handling.
- Registers lockd pernet state, generic netlink family, and procfs hooks in `init_nlm()`.
- Implements `nlmsvc_dispatch()`, the common service dispatch path used by NLM versions 1, 3, and 4.

## Key Data and State
- `nlmsvc_ops`: exported binding supplied by NFSD/NFS integration for file handle lookup/open/close callbacks.
- `nlmsvc_retry`: global timer that wakes the service when blocked lock retry work is due.
- `lockd_net_id`: pernet generic ID for `struct lockd_net`.
- `nlm_grace_period`, `nlm_timeout`, `nlm_udpport`, `nlm_tcpport`: legacy global configuration, mirrored from init net namespace for netlink updates.
- `struct lockd_net`: used here for per-net user count, configured ports, configured grace time, NSM handles, and `lockd_manager` grace-state list.

## Control Flow
`lockd_up()` serializes with `nlmsvc_mutex`, calls `lockd_get()` to create the service if necessary, then calls `lockd_up_net()` for the caller's network namespace. `lockd_up_net()` increments the per-net user count, binds the service, creates listeners, and starts the grace period. `lockd_down()` reverses the sequence with `lockd_down_net()` and `lockd_put()`.

The thread function `lockd()` initializes the service thread, marks it freezable, then loops until stopped. Each iteration retries blocked locks and receives RPC work. Shutdown invalidates client-held locks when NFS callbacks are active, shuts down host tracking, cancels grace work, ends the grace period, and exits the svc thread.

`nlmsvc_dispatch()` decodes request arguments with the procedure table, invokes the procedure handler, handles `rpc_drop_reply`, and encodes the response. Decode failure returns `rpc_garbage_args`; encode failure returns `rpc_system_err`.

## Integration Points
- Consumed by NFS/NFSD users through exported `lockd_up()` and `lockd_down()`.
- Uses SUNRPC service framework (`svc_create`, `svc_recv`, `svc_xprt_create`, rpcbind hooks).
- Uses VFS lock grace-period infrastructure from `fs/locks.c`.
- Integrates with NSM/statd host tracking through `nlm_shutdown_hosts*()` and `nsm_*` state.
- Exposes server parameters over both legacy sysctl/module parameters and newer generic netlink commands.

## Concurrency and Lifetime Notes
- Global service lifetime is protected by `nlmsvc_mutex`.
- Per-net user counts prevent destroying sockets/grace state while users remain.
- Grace-period delayed work is always canceled before ending per-net or global service state.
- Address notifier callbacks check `nlmsvc_serv` before aging transports.
- `lockd_put()` stops the service thread, deletes the retry timer synchronously, and destroys the svc service when the final global user leaves.

## Risks and Edge Cases
- `lockd_down_net()` calls `BUG()` if the per-net user count underflows, reflecting a hard lifecycle invariant.
- Port configuration has legacy global and per-net forms; init_net updates mirror into globals, while non-init namespaces only update their `lockd_net`.
- `make_socks()` destroys all xprts for the net namespace on listener setup failure.
- Authentication allows only NULL and UNIX RPC auth, and callbacks bypass `svc_set_client()` so individual procedures must do host lookup themselves.
