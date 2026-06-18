# sources/user-network-fs/samba/source4/librpc/rpc/dcerpc_connect.c

## Purpose

`dcerpc_connect.c` implements high-level DCE/RPC pipe connection orchestration. It parses or accepts bindings, maps endpoints when needed, opens the selected transport, then authenticates/binds the pipe.

## Important APIs, Types, And Functions

`struct dcerpc_pipe_connect` is the transport-open parameter bundle, holding the connection, mutable binding, interface table, credentials, resolve context, NCALRPC directory, and optional existing SMB connection/session/tree data.

Transport-specific open paths include `dcerpc_pipe_connect_ncacn_np_smb_send/recv()` for SMB named pipes, `dcerpc_pipe_connect_ncacn_ip_tcp_send/recv()` for TCP, `dcerpc_pipe_connect_ncacn_http_send/recv()` for RPC over HTTP, `dcerpc_pipe_connect_ncacn_unix_stream_send/recv()` for Unix sockets, and `dcerpc_pipe_connect_ncalrpc_send/recv()` for local RPC.

Top-level public APIs are `dcerpc_pipe_connect_b_send/recv`, `_PUBLIC_ dcerpc_pipe_connect_b()`, `dcerpc_pipe_connect_send/recv`, and `_PUBLIC_ dcerpc_pipe_connect()`.

## Control Flow

`dcerpc_pipe_connect_send()` parses a string binding and delegates to `dcerpc_pipe_connect_b_send()`. The binding-based path allocates a pipe, duplicates the binding, installs a connect timeout, determines the transport, and if no endpoint is present uses endpoint mapper lookup with anonymous credentials for NP/TCP/local and supplied credentials for HTTP. After mapping, `continue_connect()` switches on transport.

For `NCACN_NP`, it negotiates an SMB connection, chooses SMB2 or SMB1 session/tree connect based on negotiated protocol, opens the named pipe endpoint over IPC$, and stores SMBX connection/session/tcon. Binding flags can force SMB1/SMB2 or allow anonymous fallback for schannel/password-change cases. For `NCACN_IP_TCP`, it opens a TCP pipe to the endpoint port and records local/remote addresses back into the binding. For `NCACN_HTTP`, it parses options such as `HttpUseTls`, `RpcProxy`, `HttpProxy`, `HttpConnectOption`, and `HttpAuthOption`, opens ROH, and installs the returned tstream and write queue on the connection. Unix stream and NCALRPC paths require endpoint paths/names and call local open helpers.

After any transport opens, `continue_pipe_connect()` duplicates the binding into the pipe and calls `dcerpc_pipe_auth_send()`. `continue_pipe_auth()` completes the top-level composite with the authenticated pipe.

## State And Persistence Behavior

All client state is in-memory. The code mutates the binding with resolved endpoint, localaddress/host, ncalrpc_dir, and association info. It initializes `packet_log_dir` for high debug levels. Remote state includes SMB sessions/tree connects, TCP/HTTP connections, local socket handles, endpoint mapper lookups, and authenticated DCE/RPC associations.

## Dependencies And Integration Points

The file integrates composite contexts, SMB1/SMB2 clients, SMBX base, DCE/RPC open helpers, credentials, loadparm, name resolution, HTTP/ROH, endpoint mapper utilities, and transport-specific pipe open code. It is the main entry point used by generated RPC clients and tools that start from binding strings.

## Risks

Binding option parsing is broad and user-facing. The HTTP local-proxy check uses string comparison semantics that must be read carefully; incorrect truth tests can unexpectedly enable proxy mode. Endpoint mapper credential choice affects privacy and authentication. SMB fallback to anonymous is intentional for selected flags but risky if applied too broadly. Connect timeout interacts with GENSEC nested updates through inhibition flags. Transport-specific options must be validated to avoid zero ports, null endpoints, or unsupported transports.

## Test Signals

Tests should cover binding parse errors, endpoint mapper fallback, explicit endpoints, SMB1/SMB2 forced and auto negotiation, existing SMB connection reuse, TCP address recording, HTTP/ROH option parsing and auth methods, Unix and NCALRPC endpoints, unsupported transports, connect timeout, and auth bind continuation after transport open.
