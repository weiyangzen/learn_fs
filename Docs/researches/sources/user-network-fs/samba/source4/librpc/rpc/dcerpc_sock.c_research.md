# sources/user-network-fs/samba/source4/librpc/rpc/dcerpc_sock.c

## Purpose

`dcerpc_sock.c` implements socket-backed DCE/RPC transports for TCP, Unix stream sockets, and local ncalrpc-style pipe paths. It converts connected sockets into DCE/RPC `tstream` transports and handles asynchronous name resolution and address retry for TCP.

## Important APIs, Types, and Functions

Key state structs are `pipe_open_socket_state`, `pipe_tcp_state`, and `pipe_unix_state`. Important APIs are `dcerpc_pipe_open_tcp_send/recv()`, `dcerpc_pipe_open_unix_stream_send/recv()`, `dcerpc_pipe_open_pipe_send/recv()`, and synchronous `dcerpc_pipe_open_pipe()`. Shared helpers include `dcerpc_pipe_open_socket_send/recv()` and `continue_socket_connect()`.

## Control Flow

The generic socket open creates a stream socket, connects it, captures the local address and file descriptor, marks the socket no-close, wraps it in `tstream_bsd_existing_socket()`, installs the write queue, sets transport type and 5840 fragment sizes, and blocks SIGPIPE. TCP first resolves a NetBIOS name with `resolve_name_send()`, tries each resolved address until one connects, and returns actual local/remote addresses. Unix stream and ncalrpc construct Unix socket addresses; ncalrpc canonicalizes slash separators and combines an ncalrpc directory with the identifier.

## State and Persistence Behavior

Transport state is held on `struct dcecli_connection` and in talloc-owned state objects. No disk state is created. TCP stores actual local and remote address strings for binding update by secondary connection logic.

## Dependencies and Integration Points

Dependencies include Samba socket and tsocket/tstream layers, composite async contexts, resolve APIs, DCE/RPC connection internals, and transport enum values from RPC common headers. This file is called by generic connection setup and secondary connection code.

## Risks and Test Signals

Risks include address-list retry correctness, local bind failures, target-hostname null handling for local transports, Unix path canonicalization, descriptor ownership after `SOCKET_FLAG_NOCLOSE`, and SIGPIPE process-wide side effects. Test signals include DNS/NetBIOS multi-address failover, localaddress binding, IPv4/IPv6 reachability where supported, Unix/ncalrpc path opens, and simulated connect failures.
