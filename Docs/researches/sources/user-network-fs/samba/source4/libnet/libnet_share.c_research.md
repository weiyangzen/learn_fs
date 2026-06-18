# sources/user-network-fs/samba/source4/libnet/libnet_share.c

## Purpose

`libnet_share.c` implements libnet share listing, creation, and deletion over the SRVSVC RPC interface. It is a thin wrapper around generated `srvsvc_NetShareEnumAll`, `NetShareAdd`, and `NetShareDel` calls with libnet-style error strings.

## Important APIs, Types, and Functions

Public functions:
- `libnet_ListShares()` connects to `ndr_table_srvsvc`, validates requested info levels 0, 1, 2, 501, or 502, calls `srvsvc_NetShareEnumAll`, and returns the selected union share counter.
- `libnet_AddShare()` sends a level-2 `srvsvc_NetShareAdd` using `srvsvc_NetShareInfo2`.
- `libnet_DelShare()` sends `srvsvc_NetShareDel` for a named share.

## Control Flow

Each function builds a `LIBNET_RPC_CONNECT_SERVER` request for the target server and SRVSVC interface, calls `libnet_RpcConnect()`, formats `server_unc`, performs one generated RPC call, translates transport or WERROR failures into `error_string` and NTSTATUS, then frees the RPC pipe.

## State and Persistence Behavior

`ListShares` reads remote share configuration and returns counters owned by the caller's talloc context. `AddShare` and `DelShare` mutate persistent share definitions on the remote server. The implementation does not page through multiple `WERR_MORE_DATA` responses; it issues one enumeration with `max_buffer = ~0` and returns the current counter.

## Dependencies and Integration Points

The file depends on `libnet_RpcConnect`, generated SRVSVC client stubs, `srvsvc_NetShareInfo` unions, WERROR-to-NTSTATUS conversion, and Samba talloc allocation. The share API is exercised by `source4/torture/libnet/libnet_share.c`.

## Risks and Edge Cases

Enumeration accepts `WERR_MORE_DATA` as non-fatal but does not expose a useful resume handle in the implementation, even though the header has resume fields. Invalid info levels return before disconnect only if no pipe has been opened; that path is safe because validation occurs after connect but before freeing the pipe, so the current code returns early and leaks `c.out.dcerpc_pipe` for invalid levels. Add/delete require appropriate remote privileges and may produce WERROR results even when transport status is OK.

## Test Signals

Torture share tests should cover list levels, add/delete round trips, invalid info levels, duplicate adds, deleting missing shares, access-denied errors, and large enumerations that return `WERR_MORE_DATA`. Leak tests around invalid levels would be valuable.
