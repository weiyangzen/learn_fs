# sources/user-network-fs/samba/source3/rpc_server/rpc_sock_helper.c

## Purpose
This file creates listening sockets for DCE/RPC endpoint bindings. It supports named-pipe Unix sockets (`NCACN_NP`), local RPC Unix sockets (`NCALRPC`), and TCP sockets (`NCACN_IP_TCP`) for `samba-dcerpcd` endpoint setup.

## Important APIs, Types, And Functions
`dcesrv_create_ncacn_np_socket` normalizes `\pipe\` endpoints, creates the ncalrpc and `np` directories with appropriate modes, and creates the pipe socket. `dcesrv_create_ncacn_ip_tcp_socket` opens and configures a single TCP socket. `dcesrv_create_ncacn_ip_tcp_sockets` chooses explicit or dynamic ports and binds either configured interfaces or wildcard IPv4/IPv6 addresses. `dcesrv_create_ncalrpc_socket` creates local RPC sockets with role-specific defaults. Public `dcesrv_create_binding_sockets` dispatches by transport and marks returned fds close-on-exec.

## Control Flow
For named pipes and local RPC, endpoint strings are required or defaulted, directories are created, and a single Unix socket fd is returned. For TCP, the helper decides how many addresses to bind, chooses an explicit endpoint port when configured or scans `rpc low port` through `rpc high port`, attempts to bind the same port on every address, closes partial successes on conflict, and writes the selected port back into the binding endpoint string. The top-level dispatcher closes all fds and frees state on any close-on-exec failure.

## State And Persistence
Runtime fds are returned to the caller. Filesystem state includes created socket directories and socket path entries under `lp_ncalrpc_dir()`. Static `next_low_port` and `conf_high_port` persist within the process to spread dynamic TCP port choices.

## Dependencies And Integration Points
It depends on Samba socket helpers, interface enumeration, loadparm network settings, endpoint bindings, `create_pipe_sock`, and `dcesrv_core`. `rpc_host.c` calls this during endpoint setup before calling `listen`.

## Risks And Test Signals
Risks include permissions on `lp_ncalrpc_dir()/np`, stale Unix socket paths, dynamic port exhaustion, IPv4/IPv6 partial bind cleanup, and endpoint mutation being visible to endpoint mapper registration. Test signals are named-pipe socket creation with mixed-case and `\pipe\` prefixes, NCALRPC default endpoint on AD DC vs non-DC roles, TCP explicit and dynamic port binding, bind-interfaces-only behavior, and close-on-exec failure handling.
