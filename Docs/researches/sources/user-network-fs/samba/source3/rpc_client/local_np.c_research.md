# sources/user-network-fs/samba/source3/rpc_client/local_np.c

## Purpose
`local_np.c` connects Samba code to a local RPC named pipe served by `samba-dcerpcd`. It builds a named-pipe-auth request, connects to a Unix socket under the configured RPC pipe directory, performs the auth handshake, wraps the socket in an authenticated `tstream`, and starts `samba-dcerpcd` on demand when permitted and not already running.

## Important APIs, Types, And Functions
Public APIs are `local_np_connect_send()`, `local_np_connect_recv()`, and synchronous `local_np_connect()`. Internal async state machines are `np_sock_connect_send()/recv()` for socket connection/auth, and `start_rpc_host_send()/recv()` for spawning `samba-dcerpcd`. Key state structs are `np_sock_connect_state`, `start_rpc_host_state`, and `local_np_connect_state`.

## Control Flow
`local_np_connect_send()` validates the pipe name by lowercasing it and rejecting `..` or slash components, constructs `<socket_dir>/np/<pipe>`, builds a level-8 `named_pipe_auth_req`, fills transport, remote/local names and addresses, copies session info, and adds an NPA flags SID carrying `NEED_IDLE` and winbind-environment flags. It then calls `np_sock_connect_send()`.

`np_sock_connect_send()` creates a Unix socket, temporarily becomes root for connect, uses blocking connect as a workaround, switches back to nonblocking, wraps the fd in `tstream_bsd_existing_socket()`, NDR-marshals the auth request, writes it, reads a length-prefixed reply, validates level 8, and converts the stream with `tstream_npa_existing_stream()`. If initial connect fails, `local_np_connect_connected()` may spawn `samba-dcerpcd --libexec-rpcds --np-helper --ready-signal-fd=...` with `posix_spawn()` and retry once.

## State And Persistence
Runtime state is entirely per-request talloc/tevent state, socket fd ownership, copied session info, and tstream ownership. The only durable side effect is starting a helper process. It reads global configuration such as `external_rpc_pipe:socket_dir`, `rpc start on demand helpers`, dynamic config/log paths, debug level, and winbind environment.

## Dependencies And Integration Points
Dependencies include tevent async APIs, async socket connect, tsocket/tstream, named-pipe-auth NDR, NPA tstream wrappers, auth session copying, security token/SID manipulation, winbind client environment detection, loadparm, and `samba-dcerpcd`. It integrates with local RPC clients that need NCALRPC/local named-pipe access and with `source3/rpc_server/rpc_host.c`.

## Risks
The code temporarily elevates to root for Unix socket connect and process spawn, so cleanup and privilege drop paths are important. The pipe-name validation is a key path traversal guard. The initial blocking connect can stall if OS behavior changes. Adding an NPA flags SID assumes none is already present and rejects tokens containing one. On-demand spawning is intentionally disabled when config prohibits it, so callers must handle connection failure. `local_np_connect_recv()` does not call `tevent_req_received()` on success, which matches some local patterns but requires caller cleanup.

## Test Signals
Tests should cover successful connection to a running helper, start-on-demand retry, disabled start-on-demand failure, invalid pipe names, long socket paths, NPA level mismatch, session-info propagation, `need_idle_server` flag propagation, winbind-off flag behavior, and synchronous wrapper cleanup.
