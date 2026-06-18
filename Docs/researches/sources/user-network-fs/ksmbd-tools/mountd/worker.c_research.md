# sources/user-network-fs/ksmbd-tools/mountd/worker.c

## Purpose

`worker.c` is the ksmbd mount daemon's asynchronous IPC worker dispatcher. It receives kernel/userspace IPC events, pushes them into a GLib thread pool, routes each event type to the correct management subsystem, and sends IPC responses back to the server side. The source was read as a complete 387-line file.

## Important APIs, Types, and Functions

Public lifecycle/API functions are `wp_init`, `wp_destroy`, and `wp_ipc_msg_push`. Internal handlers include `login_request`, `login_request_ext`, `spnego_authen_request`, `tree_connect_request`, `share_config_request`, `tree_disconnect_request`, `logout_request`, `heartbeat_request`, and `rpc_request`. The `VALID_IPC_MSG` macro enforces exact payload size for fixed-size events. The worker binds kernel IPC structs such as `ksmbd_login_request`, `ksmbd_tree_connect_request`, `ksmbd_share_config_request`, `ksmbd_rpc_command`, and `ksmbd_spnego_authen_request` to userspace manager APIs.

## Control Flow

`wp_init` creates a `GThreadPool` with up to four workers. `wp_ipc_msg_push` queues a received `ksmbd_ipc_msg`. `worker_pool_fn` switches on `msg->type`, calls the matching handler, and frees the inbound message. Login handlers consult user management, tree handlers consult share/session management, RPC messages are delegated to `rpc_*_request`, and SPNEGO first authenticates the token before doing a normal login lookup and returning session key/blob payloads.

## State and Persistence Behavior

The file owns only the process-local thread pool. Persistent or long-lived state lives in the user, share, session, RPC, IPC, and SPNEGO modules. Response messages are heap allocated per request and freed after send.

## Dependencies and Integration Points

It depends on GLib threads, `linux/ksmbd_server.h`, `ipc.h`, `rpc.h`, and management modules for users, shares, tree connections, and SPNEGO. It is the integration boundary between kernel IPC events and ksmbd-tools userspace policy.

## Risks and Edge Cases

Some handlers dereference request payloads before or after size validation for fields such as handles/accounts, so malformed IPC sizes remain sensitive. `spnego_authen_request` reallocates the response after authentication and must free `auth_out` buffers on every path. RPC response sizing is based on command flags and `payload_sz`; incorrect handler sizes can overrun the intended IPC payload contract.

## Test Signals

Useful signals are mountd IPC integration tests for each event type, malformed-size message tests, SPNEGO success/failure paths, RPC open/read/write/ioctl smoke tests, and thread-pool shutdown tests that ensure queued messages are drained or freed cleanly.
