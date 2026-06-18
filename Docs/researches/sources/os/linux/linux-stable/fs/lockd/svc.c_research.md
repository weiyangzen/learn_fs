# File Research: sources/os/linux/linux-stable/fs/lockd/svc.c

## Summary
Central lockd service lifecycle and RPC program registration. It owns the singleton `svc_serv`, per-network-namespace lockd users, listener creation for UDP/TCP IPv4/IPv6, grace-period scheduling, module/sysctl parameters, generic netlink get/set of server settings, and common RPC dispatch.

## Main APIs
- `lockd_up()` / `lockd_down()` export global service reference management.
- `lockd()` is the service thread loop, retrying blocked NLM requests then calling `svc_recv()`.
- `lockd_up_net()` / `lockd_down_net()` bind and tear down per-net listeners and grace state.
- `nlmsvc_dispatch()` decodes, invokes, and encodes each `svc_procedure`.
- `lockd_nl_server_set_doit()` / `lockd_nl_server_get_doit()` expose per-net grace time and ports via netlink.

## Behavior
`lockd_get()` lazily creates the `svc_serv`, starts one service thread, registers address notifiers, and computes RPC buffer size from supported NLM versions. Per-net startup binds the service, creates UDP/TCP listeners, then starts a VFS lock grace period. Shutdown unwinds host state, delayed grace work, xprts, notifier registration, retry timer, and service threads.

## State and Synchronization
`nlmsvc_mutex` serializes service lifetime. Global `nlmsvc_users` and per-net `ln->nlmsvc_users` gate teardown. Grace handling uses `lockd_net.grace_period_end` delayed work and VFS `locks_start_grace()` / `locks_end_grace()`.

## Dependencies
SunRPC server APIs, network namespace storage, lockd host/resource management, procfs, generic netlink, sysctl, IPv4/IPv6 address notifiers, and NFS server binding callbacks through `nlmsvc_ops`.

## Risks
Service lifetime is split between global and per-net reference counts; mismatches can destroy xprts or the service while users remain. Callback procedures intentionally bypass early `svc_set_client()` and rely on individual procedures to look up hosts. Grace-period and listener port changes are per-net, but init-net updates also mirror legacy globals.
