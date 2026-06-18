# sources/user-network-fs/samba/source4/librpc/rpc/dcerpc_roh.h

## Purpose

`dcerpc_roh.h` defines the shared data structures, enums, and RTS command constants for Samba's RPC-over-HTTP implementation.

## Important APIs And Types

`struct roh_channel` stores connection timeout, sent byte count, channel cookie, and HTTP connection pointer. `enum roh_protocol_version` currently names `ROH_V1` and `ROH_V2`. `enum roh_connection_state` tracks open-start, out-channel wait, wait A3W, wait C2, and opened. `struct roh_connection` stores protocol version, connection state, virtual connection and association group cookies, default and non-default in/out channels, proxy-use flag, and keepalive counters.

The header also defines command type constants for RTS commands: receive-window size, flow-control ack, connection timeout, cookie, channel lifetime, client keepalive, version, empty, padding, negative/positive ANCE, client address, association group id, destination, and ping.

## Control Flow And State

The header is passive, but its state enum mirrors the connection sequence implemented in `dcerpc_roh.c`. Channel structs are updated by send/write and receive-handshake code.

## Dependencies And Integration Points

It includes generated `misc.h` for GUID and related types and forward-declares tevent queues, tstreams, and TLS params. It is included by ROH transport implementation and channel helper files.

## Risks

The state and command constants encode MS-RPCH semantics. Changing numeric constants or channel struct layout affects all ROH helpers. TODO comments in implementation mean some fields, especially non-default channels and keepalive timers, are not fully exercised.

## Test Signals

Compile tests should ensure all ROH helper files agree on the struct layout. Runtime tests should verify state transitions and command constants used in generated RTS PDUs.
