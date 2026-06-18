# sources/user-network-fs/samba/source4/librpc/rpc/dcerpc_roh_channel_out.c

## Purpose

`dcerpc_roh_channel_out.c` implements the RPC-over-HTTP outgoing channel pieces for Samba's DCE/RPC client. It sends the HTTP `RPC_OUT_DATA` request, sends the RTS `CONN/A1` PDU, reads the HTTP response, and parses RTS responses such as `CONN/A3` and `CONN/C2`.

## Important APIs, Types, and Functions

Important state structs are `roh_request_state`, `roh_send_pdu_state`, `roh_recv_response_state`, and `roh_recv_pdu_state`. Exported async pairs include `roh_send_RPC_DATA_OUT_send/recv()`, `roh_send_CONN_A1_send/recv()`, `roh_recv_out_channel_response_send/recv()`, `roh_recv_CONN_A3_send/recv()`, and `roh_recv_CONN_C2_send/recv()`.

## Control Flow

The send path builds an HTTP/1.0 RPC_OUT_DATA request to `/rpc/rpcproxy.dll?<server>:<port>`, adds RPC proxy headers, and submits it through `http_send_auth_request_send()`. `CONN/A1` constructs a DCERPC RTS packet with version, virtual connection cookie, out-channel cookie, and receive window size, marshals it with NDR, and writes it to the HTTP connection tstream queue. The receive paths call `http_read_response_send()` or `dcerpc_read_ncacn_packet_send()`, then validate RTS command counts and command types before returning timeout/window/version values.

## State and Persistence Behavior

No disk state is written. Runtime state lives under tevent request allocations and references `roh->default_channel_out`, `roh->connection_cookie`, and channel cookies. The channel's HTTP connection stream and send queue carry persistent transport state outside this file.

## Dependencies and Integration Points

This file depends on tevent, talloc, tstream, Samba HTTP helpers, NDR DCERPC marshalling, credentials/loadparm for authenticated HTTP, and `struct roh_connection` from `dcerpc_roh.h`. It is built into the `dcerpc` library and integrates with the complementary RPC-over-HTTP channel-in and high-level ROH connection code.

## Risks and Test Signals

Risks include hard-coded content length/frag length assumptions, incomplete HTTP status mapping, TODO certificate path handling, and strict RTS command ordering. Tests should cover authenticated proxy setup, 401/503 response handling, malformed RTS packets, short writes, command-count validation, and full ROH handshakes through a proxy.
