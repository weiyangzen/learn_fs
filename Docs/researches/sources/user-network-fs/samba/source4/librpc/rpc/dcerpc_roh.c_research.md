# sources/user-network-fs/samba/source4/librpc/rpc/dcerpc_roh.c

## Purpose

`dcerpc_roh.c` implements the client-side RPC-over-HTTP transport wrapper for DCE/RPC. It opens paired HTTP channels, performs the ROH/RTS connection sequence, and exposes the result as a `tstream_context` so the generic DCE/RPC engine can read and write NCACN packets without knowing about HTTP channels.

## Important APIs, Types, And Functions

`tstream_roh_ops` provides pending/readv/writev/disconnect operations. `struct tstream_roh_context` stores the `roh_connection`. `struct roh_open_connection_state` carries credentials, resolver output, DCE/RPC connection, TLS params, proxy/server addresses and ports, ROH state, loadparm, and HTTP auth method.

Public open functions are `dcerpc_pipe_open_roh_send()` and `dcerpc_pipe_open_roh_recv()`. Channel helpers include `roh_connect_channel_send/recv()`. The connection sequence uses helpers from companion files: `roh_send_RPC_DATA_IN`, `roh_send_RPC_DATA_OUT`, `roh_send_CONN_A1`, `roh_send_CONN_B1`, `roh_recv_out_channel_response`, `roh_recv_CONN_A3`, and `roh_recv_CONN_C2`.

The tstream adapter maps reads to the default out channel and writes to the default in channel. Disconnect tears down channel-in first, then channel-out.

## Control Flow

`dcerpc_pipe_open_roh_send()` initializes a version-2 ROH connection with random virtual connection and association group cookies, optional TLS parameters, proxy-use flags, and keepalive counters. It resolves the RPC proxy, opens an HTTP connection for the in channel, opens another for the out channel, sends the RPC_IN_DATA HTTP request, sends the RPC_OUT_DATA request, sends RTS CONN/A1 and CONN/B1 PDUs, waits for the out-channel HTTP response, receives CONN/A3, receives CONN/C2, marks the connection opened, and completes.

`dcerpc_pipe_open_roh_recv()` wraps the opened ROH connection in a tstream with `tstream_roh_ops` and returns the send queue from the default in channel's HTTP connection. The DCE/RPC core then uses normal tstream reads/writes.

## State And Persistence Behavior

State is in-memory and tied to the returned tstream. `roh_connection` stores protocol version, connection state, cookies, channel pointers, proxy-use and keepalive values. Each `roh_channel` tracks connection timeout, sent bytes, channel cookie, and HTTP connection. No local persistence occurs.

## Dependencies And Integration Points

The file integrates `tevent`, tsocket internals, TLS params, name resolution, credentials, loadparm, HTTP client helpers, DCE/RPC ROH structs, and generic DCE/RPC connection setup in `dcerpc_connect.c`.

## Risks

ROH setup is order-sensitive: the two HTTP channels and RTS PDUs must be sequenced exactly. The code currently resolves proxy names and uses the first address only; fallback to later addresses is not implemented in the observed flow. TODOs note virtual connection cookie table, proxy discovery, timers, and v1 fallback are incomplete. The returned stream depends on both channels remaining valid; partial disconnect or channel allocation failure must propagate `ENOTCONN`.

## Test Signals

Tests should mock HTTP connections to verify request order, TLS versus non-TLS paths, proxy option handling, failure at each handshake stage, read-from-out/write-to-in stream mapping, sent byte accounting, disconnect order, and behavior when channel pointers are null.
