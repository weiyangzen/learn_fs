<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/MainNFSD/9p_rdma_dispatcher.c -->
# sources/user-network-fs/nfs-ganesha/src/MainNFSD/9p_rdma_dispatcher.c

## Purpose
Starts and manages the 9P/RDMA listener using Mooshika. It allocates global output pools, registers per-NIC input/output memory, accepts child transports, initializes `_9p_conn`, and finalizes RDMA accepts.

## Important APIs, Types, And Functions
- `_9p_rdma_dispatcher_thread()` configures, binds, and accepts Mooshika transports.
- `_9p_rdma_thread()` initializes per-connection private data and calls `msk_finalize_accept()`.
- `_9p_rdma_setup_global()` allocates shared output buffer pool and outqueue.
- `_9p_rdma_setup_pernic()` registers memory and posts initial receives.
- `_9p_rdma_cleanup_conn_thread()` and `_9p_rdma_cleanup_conn()` are intended cleanup paths.

## Control Flow
The dispatcher creates server transport attributes from `_9p_param`, starts/binds Mooshika, then loops on `msk_accept_one()`. The first child creates global output buffers. Each child gets per-NIC receive setup, inherits the shared outqueue as initial private data, and is finalized by a detached `_9p_rdma_thread()`.

## State And Persistence Behavior
State is in memory and transport-bound: registered memory, input/output pools, outqueue mutex/condvar, fids, flush buckets, client refs, and transport private data. No persistence.

## Dependencies And Integration Points
Depends on Mooshika, RDMA callbacks, shared 9P queues, client manager, RCU, and 9P config parameters from daemon initialization.

## Risks
- `_9p_rdma_cleanup_conn()` returns before spawning cleanup, making cleanup unreachable.
- `iPTHREAD_ATTR_setdetachstate` appears typo-like unless defined as a macro.
- `_9p_rdma_thread()` destroys flush-bucket mutexes on normal exit while the connection may still be active.
- Peer address copy can truncate IPv6 address data.
- Dispatcher loop has no shutdown path.

## Test Signals
Build with RDMA enabled, connect/disconnect under leak detection, verify receive posting and send reuse, check IPv6 peer storage, and stress disconnect with active worker refs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/MainNFSD/9p_rdma_dispatcher.c -->
