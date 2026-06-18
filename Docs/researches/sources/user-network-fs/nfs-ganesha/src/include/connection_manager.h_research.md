# sources/user-network-fs/nfs-ganesha/src/include/connection_manager.h

## Purpose
`connection_manager.h` declares the clustered connection manager that ensures an NFS client is active on only one Ganesha server at a time. It mitigates NFSv4 exactly-once-semantics hazards when load balancing can move a client before older requests finish on another server.

## Important APIs, Types, And Functions
The API centers on `connection_manager__client_t`, embedded in `gsh_client`, and `connection_manager__connection_t`, embedded in XPRT custom data. Important enums are drain results, registration results, client states (`DRAINED`, `ACTIVATING`, `ACTIVE`, `DRAINING`), and connection-start results. Callback types register/deregister connections and drain other servers. Public functions set/clear callbacks, initialize the module and per-client state, initialize/start/finish connections, test drain success, and drain local client connections.

## Control Flow
New XPRTs call `connection_manager__connection_init`, then `connection_manager__connection_started` after the client address is known. If connection management is disabled or the address is loopback, the connection is allowed unmanaged. For managed clients, `DRAINED` transitions to `ACTIVATING`, invokes the cluster callback to register and drain other servers, then becomes `ACTIVE` or reverts to `DRAINED`. Active clients register additional connections directly. A local drain request transitions `ACTIVE` to `DRAINING`, sets TCP linger to RST quickly, calls `SVC_DESTROY` on each connection, waits for connection finish notifications, and then marks the client `DRAINED` or `ACTIVE` depending on remaining connections.

## State And Persistence
State is in memory: per-client mutex, condition variable, list of managed connections, connection count, per-connection XPRT/client pointers, destruction flag, and destroy start time. Metrics are updated for states, connection-start latency/result, and drain latency/result. No state is persisted across restart; cluster registration persistence is delegated to callbacks.

## Dependencies And Integration Points
The header depends on `common_utils.h`, RPC `SVCXPRT`, `gsh_client`, `network_id`, and Ganesha socket utilities. Implementation integrates with `client_mgr.c`, `xprt_handler.h`, `connection_manager_metrics`, `nfs_param.core_param.enable_connection_manager`, callback providers for cluster coordination, and LTTng tracepoints.

## Risks
Correctness depends on callback implementations being registered before managed traffic arrives and on callbacks deregistering exactly once after successful registration. The header documents lease extension after drain, but implementation currently carries a TODO, so reclaim windows are a known correctness risk. New incoming connections abort local draining by moving `DRAINING` back to `ACTIVE`, which is intentional priority behavior but must be understood by cluster callbacks. Stuck destroyed connections are detected only after timeout multiples.

## Test Signals
Tests should cover disabled manager, loopback bypass, callback default refusal, successful first activation, concurrent activation waiters, additional active connections, drain with no local client, drain of active connections, drain aborted by new connection, timeout/stuck detection, deregister-on-finish, callback clear/set assertions, and metrics label updates.
