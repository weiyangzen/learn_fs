# sources/user-network-fs/nfs-ganesha/src/include/nfs_core.h

## Purpose

`nfs_core.h` declares central server runtime state and service-thread interfaces: host identity, callback RPC call structures, health counters, event channels, boot/write verifiers, config blocks, admin thread controls, RPC transport initialization, worker selection, reaper lifecycle, and optional 9P/RDMA hooks.

## Important APIs, Types, and Functions

Important globals include `nfs_host_name`, `cid_server_owner`, `cid_server_scope`, `nfs_health_`, `nfs_ServerBootTime`, `nfs_ServerEpoch`, NFS write verifiers, config paths, netconfig pointers, `admin_shutdown`, and parsed config blocks. `nfs4_compound_t`, `rpc_call_t`, and `rpc_call_func` model outbound callback RPC calls. Core functions initialize/destroy RPC (`nfs_Init_netconfig`, `nfs_Init_svc`, `Clean_RPC`, `nfs_rpc_dispatch_stop`), select event/worker channels, manage admin and reaper threads, encode/decode base64, compare state IDs, and destroy callback channels.

## Control Flow

Startup initializes netconfigs, service sockets, config blocks, admin thread, and reapers. Dispatch uses event channel IDs and worker queues; callback code uses `rpc_call_t` and `rpc_call_channel_t` from `nfs_proto_data.h`. Shutdown stops dispatch, admin, reapers, and RPC channels.

## State and Persistence Behavior

State is process-global and long-lived: boot epoch, verifiers, health counters, config paths, netconfigs, admin state, RPC channels, and reaper state. Boot/write verifier values are externally visible to clients for cache and write stability semantics.

## Dependencies and Integration Points

It depends on SAL data, Ganesha config, optional GSS, optional 9P/RDMA, and error injection. It integrates with initialization, worker dispatch, callback RPC, DBus diagnostics, NFSv4 state/session handling, and cleanup.

## Risks and Test Signals

Risks include global initialization order, shutdown races, callback channel lifetime, incorrect boot epoch/verifier changes, event-channel bounds, and optional-feature compile paths. Tests should cover startup/shutdown cycles, health counter behavior, netid lookup, worker queue selection distribution, reaper wake/shutdown, callback channel destruction, and builds with GSS/9P/RDMA toggles.
