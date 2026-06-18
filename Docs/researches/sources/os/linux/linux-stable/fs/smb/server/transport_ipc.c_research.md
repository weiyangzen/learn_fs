# File Research: sources/os/linux/linux-stable/fs/smb/server/transport_ipc.c

## Summary
Implements ksmbd’s generic-netlink IPC channel to the user-space ksmbd daemon. It handles daemon startup configuration, synchronous request/response correlation, authentication and share lookups, SPNEGO authentication, named-pipe RPC forwarding, heartbeat timeout detection, IPC ids, and netlink family registration.

## Main Responsibilities
- Register the `KSMBD_GENL_NAME` generic-netlink family and supported event operations.
- Validate daemon/kernel IPC protocol version.
- Receive startup configuration from user space and apply server settings: limits, flags, signing, ports, protocol bounds, SMB2 sizes, RDMA size, domain SID, names, workgroup, and interface binding.
- Track daemon port id and heartbeat activity, resetting the server if the daemon stops responding.
- Allocate IPC messages and correlate synchronous responses through a hash table keyed by request handle.
- Validate response payload sizes for RPC, SPNEGO, share config, and extended login responses.
- Send login, extended login, share config, tree connect/disconnect, logout, SPNEGO, and RPC open/read/write/ioctl/close requests.
- Enforce payload limits and account/share-name length limits.

## Key Interfaces
- Authentication/config: `ksmbd_ipc_login_request()`, `ksmbd_ipc_login_request_ext()`, `ksmbd_ipc_share_config_request()`, `ksmbd_ipc_spnego_authen_request()`.
- Tree/session notifications: `ksmbd_ipc_tree_connect_request()`, `ksmbd_ipc_tree_disconnect_request()`, `ksmbd_ipc_logout_request()`.
- RPC forwarding: `ksmbd_ipc_id_alloc()`, `ksmbd_rpc_id_free()`, `ksmbd_rpc_open()`, `ksmbd_rpc_close()`, `ksmbd_rpc_write()`, `ksmbd_rpc_read()`, `ksmbd_rpc_ioctl()`.
- Lifecycle: `ksmbd_ipc_init()`, `ksmbd_ipc_release()`, `ksmbd_ipc_soft_reset()`.

## Important Behavior
Requests that expect responses create an `ipc_msg_table_entry`, publish it under `ipc_msg_table_lock`, send a netlink message to the daemon, and wait up to `IPC_WAIT_TIMEOUT`. Responses are accepted only if the type equals request type plus one and the payload length matches event-specific validation.

Startup is serialized with `startup_lock`. If a daemon is already registered, the kernel checks liveness with a heartbeat before accepting a replacement daemon. Heartbeat work uses `server_conf.ipc_timeout` and schedules server reset when the daemon is inactive.

RPC operations include session-derived method flags and restricted context for guest users. Write/ioctl payloads are capped by `KSMBD_IPC_MAX_PAYLOAD`.

## Cross-File Interactions
Feeds configuration into `server_conf`, TCP interface setup, RDMA sizing, SMB2 max size/credit settings, file descriptor limits, and domain SID initialization. Used by user/session/share/tree management and IPC named-pipe RPC paths.

## Risks
This is a kernel/user trust boundary. Response size validation, handle correlation, version checking, daemon liveness, netlink capability checks, and payload length caps are security-critical. Races around daemon replacement, reset, and pending request wakeups can affect server availability.
