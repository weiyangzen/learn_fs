# sources/user-network-fs/impacket/impacket/dcerpc/v5/rpcrt.py

## Purpose

`rpcrt.py` is Impacket's core partial implementation of connection-oriented DCE/RPC v5 runtime behavior. It defines PDU constants, status-code tables, packet structures, bind and alter-context negotiation, authenticated send/receive handling for NTLM, Netlogon, and Kerberos/SPNEGO, request/response dispatch, fragmentation/reassembly, object UUID calls, type serialization headers, and a minimal DCE/RPC server used by SMB server and relay scenarios.

## Important APIs, Types, And Functions

The public surface includes PDU type constants, packet flags, authentication provider and level constants, `rpc_status_codes`, many named `MSRPC_STATUS_CODE_*` constants, bind-time feature negotiation constants, and `MSRPC_STANDARD_NDR_SYNTAX`. `DCERPCException` is the common runtime exception for transports and protocol modules.

Packet and bind structures include `CtxItem`, `CtxItemResult`, `SEC_TRAILER`, `MSRPCHeader`, `MSRPCRequestHeader`, `MSRPCRespHeader`, `MSRPCBind`, `MSRPCRelayBind`, `MSRPCBindAck`, `MSRPCRelayBindAck`, and `MSRPCBindNak`. Runtime classes are `DCERPC`, `DCERPC_v4`, `DCERPC_v5`, `DCERPC_RawCall`, and `DCERPCServer`. Type serialization helpers are `CommonHeader`, `PrivateHeader`, and `TypeSerialization1`.

Important `DCERPC_v5` APIs include `set_credentials`, `get_credentials`, `set_auth_level`, `set_auth_type`, `get_auth_type`, `set_aes`, `set_session_key`, `get_session_key`, `set_max_tfrag`, `bind`, `send`, `recv`, and `alter_ctx`. `DCERPC.request()` implements the common NDR call pattern used by almost every protocol binding in `impacket.dcerpc.v5`.

## Control Flow

`DCERPC.request()` adapts the request for NDR64 when needed, calls the request opnum, receives bytes, imports the request module, locates the matching `*Response` class, and either returns a decoded response or raises a module-specific `DCERPCSessionError`/runtime exception based on the final four-byte error code.

`DCERPC_v5.bind()` builds one or more presentation context items, optionally prepending bogus contexts, then sends a bind or alter-context PDU. If authentication is enabled, it obtains credentials, builds a Type 1 token for NTLM, Netlogon, or Kerberos, appends a security trailer, and sends the bind. It parses bind acknowledgments or faults, validates accepted context results, stores the selected transfer syntax and negotiated max transmit size, completes authentication with NTLM Type 3, Netlogon, or Kerberos continuation tokens, initializes signing/sealing keys and sequence state, and sends AUTH3 or Kerberos alter-context continuation when required.

`send()` wraps raw calls, sets call ID, context ID, object UUID flags, and allocation hint, decides whether fragmentation is needed based on negotiated and user fragment sizes, emits first/middle/last fragments, and signs or seals each fragment through `_transport_send()`. `_transport_send()` adds security trailers, computes padding, signs or encrypts payloads for packet integrity or privacy, increments sequence numbers, and delegates to the underlying transport. `recv()` reads full response fragments, handles faults, strips and verifies/decrypts authentication trailers when configured, removes auth padding, reassembles fragments, and returns stub data.

`DCERPCServer` accepts sockets, parses bind requests, validates transfer syntax and registered interface UUIDs, returns bind acks, dispatches request opnums to registered callbacks, returns faults for unsupported opnums, and fragments server responses when needed.

## State And Persistence Behavior

There is no disk persistence. Client runtime state includes transport, context ID, call ID, negotiated transfer syntax, max transmit size, credentials, authentication type and level, session key, signing/sealing keys and ARC4 handles, Netlogon confounder, Kerberos GSS wrapper, sequence number, and max user fragment setting. `alter_ctx()` creates a new runtime object sharing the same underlying transport and credentials but with a new context.

Server state includes listening socket, bound UUID, callback registry, current client socket, call ID, listen address/port, and fragmentation settings. Registered callbacks persist in memory until the server object is discarded.

## Dependencies And Integration Points

The module depends on sockets, logging, threading, `Cryptodome.Cipher.ARC4`, Impacket NTLM, Kerberos, GSSAPI, UUID helpers, `Structure` packing/unpacking, `dtypes`, NDR structures, HRESULT errors, and `LOG`. Every DCE/RPC protocol binding in this directory depends on `DCERPCException` and `DCERPC_v5.request()` semantics. Transports from `impacket.dcerpc.v5.transport` supply the actual SMB, TCP, HTTP, or local communication layer.

## Risks And Edge Cases

This file is security-critical because authentication, signing, sealing, fault handling, and fragmentation all converge here. Several comments flag incomplete behavior: receive-side NTLM packet privacy with extended session security says signature calculation needs fixing, and fragmentation sizing uses a broad 128-byte trailer estimate. Kerberos and Netlogon sequence handling has provider-specific branches that are easy to regress. `DCERPC.request()` assumes non-error NDR responses end with four zero bytes, which can be brittle for unusual stubs.

Parsing and compatibility risks include manual PDU length calculations, object UUID header-size adjustments, auth trailer padding, and fixed assumptions about connection-oriented NDR32/NDR64 syntax. `MSRPCBind.getData()` and related structures append to `ctx_items` without clearing it, so repeated serialization of the same object can duplicate context bytes. The minimal server ignores authentication and only supports NDR32 in bind acceptance. Some server paths set padding as text strings instead of bytes, which can be problematic under strict Python 3 byte handling.

## Test Signals

Unit tests should cover PDU structure round trips, bind context item construction, bind ack parsing, bind rejection messages, request response class lookup, module-specific error raising, object UUID calls, fragmentation boundaries, and repeated `getData()` calls on bind structures. Auth tests should use known NTLM, Netlogon, and Kerberos fixtures for connect, integrity, and privacy levels. Transport tests should simulate multi-fragment responses, faults with RPC and HRESULT codes, auth padding, and short reads. Server tests should bind supported and unsupported interfaces, dispatch known and unknown opnums, and verify response fragmentation.
