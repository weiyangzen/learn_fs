# sources/user-network-fs/impacket/impacket/dcerpc/v5/iphlp.py

## Purpose

`iphlp.py` implements selected MSRPC calls exposed by `iphlpsvc.dll` for IPv6 transition technologies over IPv4 networks. It supports applying transition configuration-change notifications and creating or deleting IPv6-in-IPv4 tunnels.

## Important APIs, Types, And Functions

The module exports `MSRPC_UUID_IPHLP_IP_TRANSITION`, `MSRPC_UUID_IPHLP_TEREDO`, `MSRPC_UUID_IPHLP_TEREDO_CONSUMER`, `DCERPCSessionError`, notification constants, `BYTE_ARRAY`, and four RPC operations. Call classes are `IpTransitionProtocolApplyConfigChanges` opnum 0, `IpTransitionProtocolApplyConfigChangesEx` opnum 1, `IpTransitionCreatev6Inv4Tunnel` opnum 2, and `IpTransitionDeletev6Inv4Tunnel` opnum 3. Helpers wrap all four.

## Control Flow

Notification helpers assign notification number and optional data length/data, then call `dce.request()`. Tunnel creation converts local and remote IPv4 addresses with `inet_aton`, null-terminates the interface name, sets nested `InterfaceName.MaximumCount` to 256, and sends the request. Tunnel deletion converts a textual GUID to binary and sends opnum 3.

## State And Persistence Behavior

There is no local persistence. Remote operations can mutate network configuration by creating/deleting tunnels or triggering service configuration refreshes. The Ex notification path notes no admin is required for the DirectAccess site manager local configuration change notification. The module does not track created tunnel GUIDs or rollback state.

## Dependencies And Integration Points

Dependencies include `socket.inet_aton`, Impacket `uuid`, HRESULT errors, UUID conversion, common dtypes (`BYTE`, `ULONG`, `WSTR`, `GUID`, `NULL`), NDR classes, and `DCERPCException`. It integrates with IP Helper service RPC interfaces and can use endpoint discovery via `epm.py`.

## Risks And Edge Cases

Operations can disrupt remote network configuration. Invalid IPv4 strings fail locally. `checkNullString` assumes string-like input. For tunnel creation, forcing `MaximumCount` to 256 is protocol-specific but does not validate long names. Teredo UUIDs are declared but Teredo-specific calls are not modeled.

## Test Signals

Tests should mock DCE requests and verify opnums, notification fields, data lengths, IPv4 byte order, interface null termination, `MaximumCount`, and GUID conversion. Negative tests should cover invalid addresses, invalid GUIDs, empty interface names, and `NULL` handling. Integration tests should run only on isolated Windows targets and verify cleanup.
