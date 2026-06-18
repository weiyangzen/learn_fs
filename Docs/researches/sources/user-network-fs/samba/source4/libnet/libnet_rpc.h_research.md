# sources/user-network-fs/samba/source4/libnet/libnet_rpc.h

## Purpose

`libnet_rpc.h` declares the libnet RPC connection request/response ABI. It gives callers a single level-tagged structure for connecting to standalone servers, specific addresses, DCs, PDCs, explicit binding strings, or DCs with discovered domain metadata.

## Important APIs, Types, and Functions

`enum libnet_RpcConnect_level` defines `LIBNET_RPC_CONNECT_SERVER`, `SERVER_ADDRESS`, `PDC`, `DC`, `BINDING`, and `DC_INFO`. `struct libnet_RpcConnect` holds input `name`, `address`, `binding`, `dcerpc_iface`, and `dcerpc_flags`; output `dcerpc_pipe`, optional `domain_name`, `domain_sid`, `realm`, `guid`, and `error_string`.

`struct msg_net_rpc_connect` is the monitor payload with host, target domain name, endpoint, and DCERPC transport.

## Control Flow

The header is declarative. Its level enum drives the dispatcher in `libnet_rpc.c`, while its output fields let DC-info callers receive both the pipe and LSA-discovered metadata in one operation.

## State and Persistence Behavior

Callers supply the structure and memory context. On success, implementation stores a talloc-owned `dcerpc_pipe` and optional metadata under the requested output context and may also cache references in `libnet_context`.

## Dependencies and Integration Points

The header includes `librpc/rpc/dcerpc.h` and is included by `libnet/libnet.h` consumers throughout source4 libnet. It couples callers to NDR interface-table pointers and DCERPC transport enums.

## Risks and Edge Cases

Callers must set a compatible combination of level and input fields: server-address needs both `address` and `name`, binding needs `binding`, and DC/PDC needs a domain `name`. `dcerpc_flags` are meaningful only on paths that apply them. Output metadata is only valid for `DC_INFO`.

## Test Signals

Compile-time coverage plus the libnet RPC torture tests are the main signal. Any change to enum order or structure fields can break ABI expectations in C and Python-adjacent callers.
